"""Summarize command for hlpr CLI."""

import json
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

from hlpr.config import CONFIG
from hlpr.document.parser import DocumentParser
from hlpr.document.summarizer import DocumentSummarizer
from hlpr.exceptions import (
    ConfigurationError,
    DocumentProcessingError,
    HlprError,
    SummarizationError,
)
from hlpr.models.document import Document

# Create typer app for summarize commands
app = typer.Typer(help="Document summarization commands")

# Console for rich output
console = Console()


@app.command("document")
def summarize_document(  # noqa: PLR0913 - CLI keeps multiple options for UX
    file_path: str = typer.Argument(..., help="Path to the document file to summarize"),
    provider: str = typer.Option(
        "local",
        "--provider",
        help=(
            "AI provider to use [local|openai|anthropic|groq|together]"
        ),
    ),
        save: bool = typer.Option(  # noqa: FBT001 - boolean CLI flag is conventional
            default=False,
            help="Save summary to file",
        ),
    output_format: str = typer.Option(
        "rich",
        "--format",
        help="Output format [txt|md|json|rich]",
    ),
    output: str | None = typer.Option(
        None,
        "--output",
        help="Output file path",
    ),
    chunk_size: int = typer.Option(
        8192,
        "--chunk-size",
        help="Chunk size for large documents",
    ),
    chunk_overlap: int = typer.Option(
        256,
        "--chunk-overlap",
        help="Overlap between chunks",
    ),
    chunking_strategy: str = typer.Option(
        "sentence",
        "--chunking-strategy",
        help=(
            "Chunking strategy [sentence|paragraph|fixed|token]"
        ),
    ),
    verbose: bool = typer.Option(  # noqa: FBT001 - boolean CLI flag is conventional
        default=False,
        help="Enable verbose output",
    ),
    model: str = typer.Option(
        "gemma3:latest",
        "--model",
        help="Model name to use (e.g., gemma3:latest)",
    ),
    temperature: float = typer.Option(
        0.3,
        "--temperature",
        help="Sampling temperature for the model (0.0-1.0)",
    ),
    dspy_timeout: int | None = typer.Option(
        None,
        "--dspy-timeout",
        help="DSPy request timeout in seconds (falls back to HLPR_DEFAULT_TIMEOUT)",
    ),
    no_fallback: bool = typer.Option(  # noqa: FBT001 - boolean CLI flag is conventional
        default=False,
        help="Disable fallback to local summarizer on DSPy failure",
    ),
    verify_hallucinations: bool = typer.Option(  # noqa: FBT001 - boolean CLI flag is conventional
        default=False,
        help="Verify flagged hallucinations with additional model calls",
    ),
):
    """Summarize a document (PDF, DOCX, TXT, MD)."""
    # Validate file exists (outside try to avoid TRY301)
    path = Path(file_path)
    if not path.exists():
        console.print(f"[red]Error:[/red] File not found: {file_path}")
        raise typer.Exit(1)

    if not path.is_file():
        console.print(f"[red]Error:[/red] Path is not a file: {file_path}")
        raise typer.Exit(1)

    try:
        document, extracted_text = _parse_with_progress(file_path, verbose)

        # Initialize summarizer (use CONFIG.default_timeout when not provided)
        timeout_val = (
            dspy_timeout if dspy_timeout is not None else CONFIG.default_timeout
        )
        summarizer = DocumentSummarizer(
            provider=provider,
            model=model,
            temperature=temperature,
            api_base=None,
            api_key=None,
            timeout=timeout_val,
            no_fallback=no_fallback,
            verify_hallucinations=verify_hallucinations,
        )

        # Summarize with progress
        result = _summarize_with_progress(
            summarizer,
            document,
            extracted_text,
            chunk_size,
            chunk_overlap,
            chunking_strategy,
            verbose,
        )

        # Display results
        _display_summary(document, result, output_format)

        # Save to file if requested
        if save:
            output_path = _save_summary(document, result, output_format, output)
            console.print(f"\n[green]Summary saved to:[/green] {output_path}")

    except typer.Exit:
        raise
    except HlprError as he:
        # Map domain errors to CLI exit codes for clearer automation handling
        if isinstance(he, DocumentProcessingError):
            console.print(f"[red]Document error:[/red] {he}")
            raise typer.Exit(6) from he
        if isinstance(he, SummarizationError):
            console.print(f"[red]Summarization error:[/red] {he}")
            raise typer.Exit(5) from he
        if isinstance(he, ConfigurationError):
            console.print(f"[red]Configuration error:[/red] {he}")
            raise typer.Exit(2) from he
        # Fallback for generic HlprError
        console.print(f"[red]Error:[/red] {he}")
        raise typer.Exit(3) from he
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise typer.Exit(4) from e


def _display_summary(document: Document, result: Any, output_format: str) -> None:  # noqa: C901,PLR0912,PLR0915
    """Display the summary results in the specified format."""
    if output_format == "rich":
        # Rich terminal display
        summary_panel = Panel(
            result.summary,
            title="[bold blue]Summary[/bold blue]",
            border_style="blue",
        )
        console.print(summary_panel)

        if result.key_points:
            key_points_text = "\n".join(
                f"• {point}" for point in result.key_points
            )
            key_points_panel = Panel(
                key_points_text,
                title="[bold green]Key Points[/bold green]",
                border_style="green",
            )
            console.print(key_points_panel)

        # Metadata
        metadata = Text()
        metadata.append(f"File: {Path(document.path).name}\n")
        metadata.append(f"Format: {document.format.value.upper()}\n")
        metadata.append(f"Size: {document.size_bytes:,} bytes\n")
        metadata.append(f"Processing time: {result.processing_time_ms}ms\n")
        metadata.append("Provider: {}".format(getattr(result, "provider", "unknown")))

        metadata_panel = Panel(
            metadata,
            title="[bold yellow]Metadata[/bold yellow]",
            border_style="yellow",
        )
        console.print(metadata_panel)

        # Show hallucination warnings if any
        if getattr(result, "hallucinations", None):
            warn_text = "\n".join(result.hallucinations[:5])
            console.print(
                Panel(
                    warn_text,
                    title="[bold red]Potential Hallucinations[/bold red]",
                    border_style="red",
                ),
            )

    elif output_format == "json":
        # JSON output
        output_data = {
            "file": str(Path(document.path).name),
            "format": document.format.value,
            "size_bytes": document.size_bytes,
            "summary": result.summary,
            "key_points": result.key_points,
            "hallucinations": getattr(result, "hallucinations", []),
            "processing_time_ms": result.processing_time_ms,
        }
        console.print_json(data=output_data)

    elif output_format == "txt":
        # Plain text output
        console.print(f"Document: {Path(document.path).name}")
        console.print(f"Format: {document.format.value.upper()}")
        console.print(f"Size: {document.size_bytes:,} bytes")
        console.print(f"Processing time: {result.processing_time_ms}ms")
        console.print()
        console.print("SUMMARY:")
        console.print(result.summary)
        console.print()
        if result.key_points:
            console.print("KEY POINTS:")
            for point in result.key_points:
                console.print(f"• {point}")

        if getattr(result, "hallucinations", None):
            console.print("\nPOTENTIAL HALLUCINATIONS:")
            for h in result.hallucinations:
                console.print(f"- {h}")

    elif output_format == "md":
        # Markdown output
        console.print(f"# Document Summary: {Path(document.path).name}")
        console.print()
        console.print(f"- **Format**: {document.format.value.upper()}")
        console.print(f"- **Size**: {document.size_bytes:,} bytes")
        console.print(f"- **Processing time**: {result.processing_time_ms}ms")
        console.print()
        console.print("## Summary")
        console.print()
        console.print(result.summary)
        console.print()
        if result.key_points:
            console.print("## Key Points")
            console.print()
            for point in result.key_points:
                console.print(f"- {point}")
        if getattr(result, "hallucinations", None):
            console.print("## Potential Hallucinations")
            console.print()
            for h in result.hallucinations:
                console.print(f"- {h}")


def _save_summary(
    document: Document,
    result: Any,
    output_format: str,
    output_path: str | None,
) -> str:
    """Save the summary to a file."""
    save_path = _determine_output_path(document, output_format, output_path)

    # Ensure we don't overwrite without warning
    if save_path.exists():
        warn_msg = f"Overwriting existing file: {save_path}"
        console.print(f"[yellow]Warning:[/yellow] {warn_msg}")

    content = _format_summary_content(document, result, output_format)

    # Write to file
    with save_path.open("w", encoding="utf-8") as f:
        f.write(content)

    return str(save_path)


def _determine_output_path(
    document: Document, output_format: str, output_path: str | None,
) -> Path:
    """Compute output file path based on format and user input."""
    if output_path:
        return Path(output_path)

    doc_name = Path(document.path).stem
    if output_format == "json":
        return Path(f"{doc_name}_summary.json")
    if output_format == "md":
        return Path(f"{doc_name}_summary.md")
    return Path(f"{doc_name}_summary.txt")


def _format_summary_content(document: Document, result: Any, output_format: str) -> str:
    """Generate summary content in the requested format."""
    if output_format == "json":
        output_data = {
            "file": str(Path(document.path).name),
            "format": document.format.value,
            "size_bytes": document.size_bytes,
            "summary": result.summary,
            "key_points": result.key_points,
            "processing_time_ms": result.processing_time_ms,
        }
        return json.dumps(output_data, indent=2)

    if output_format == "md":
        content = f"# Document Summary: {Path(document.path).name}\n\n"
        content += f"- **Format**: {document.format.value.upper()}\n"
        content += f"- **Size**: {document.size_bytes:,} bytes\n"
        content += f"- **Processing time**: {result.processing_time_ms}ms\n\n"
        content += "## Summary\n\n"
        content += f"{result.summary}\n\n"
        if result.key_points:
            content += "## Key Points\n\n"
            for point in result.key_points:
                content += f"- {point}\n"
        return content

    # txt or rich
    content = f"Document: {Path(document.path).name}\n"
    content += f"Format: {document.format.value.upper()}\n"
    content += f"Size: {document.size_bytes:,} bytes\n"
    content += f"Processing time: {result.processing_time_ms}ms\n\n"
    content += "SUMMARY:\n"
    content += f"{result.summary}\n\n"
    if result.key_points:
        content += "KEY POINTS:\n"
        for point in result.key_points:
            content += f"• {point}\n"
    return content


def _parse_with_progress(file_path: str, verbose: bool) -> tuple[Document, str]:  # noqa: FBT001
    """Parse the document file with a progress indicator and return model+text."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        disable=not verbose,
    ) as progress:
        parse_task = progress.add_task("Parsing document...", total=None)
        try:
            extracted_text = DocumentParser.parse_file(file_path)
            desc = "Document parsed successfully"
            progress.update(parse_task, completed=True, description=desc)
        except DocumentProcessingError as e:
            # Domain parser errors: map unsupported formats to exit code 2,
            # other document processing failures map to exit code 6.
            msg = str(e).lower()
            if "unsupported" in msg or "unsupported file format" in msg:
                err_msg = f"Unsupported file format: {e}"
                desc = f"Unsupported format: {e}"
                progress.update(parse_task, completed=True, description=desc)
                console.print(f"[red]Error:[/red] {err_msg}")
                raise typer.Exit(2) from e
            err_msg = f"Failed to parse document: {e}"
            desc = err_msg
            progress.update(parse_task, completed=True, description=desc)
            console.print(f"[red]Error:[/red] {err_msg}")
            raise typer.Exit(6) from e
        except ValueError as e:
            # Backwards-compatible handling for older code paths that raised
            # ValueError for unsupported formats — keep existing behavior.
            msg = str(e).lower()
            if "unsupported" in msg or "unsupported file format" in msg:
                err_msg = f"Unsupported file format: {e}"
                desc = f"Unsupported format: {e}"
                progress.update(parse_task, completed=True, description=desc)
                console.print(f"[red]Error:[/red] {err_msg}")
                raise typer.Exit(2) from e
            err_msg = f"Failed to parse document: {e}"
            desc = err_msg
            progress.update(parse_task, completed=True, description=desc)
            console.print(f"[red]Error:[/red] {err_msg}")
            raise typer.Exit(6) from e
        except Exception as e:
            err_msg = f"Failed to parse document: {e}"
            progress.update(parse_task, completed=True, description=err_msg)
            console.print(f"[red]Error:[/red] {err_msg}")
            raise typer.Exit(6) from e

    document = Document.from_file(file_path)
    document.extracted_text = extracted_text
    return document, extracted_text


def _summarize_with_progress(  # noqa: PLR0913
    summarizer: DocumentSummarizer,
    document: Document,
    extracted_text: str,
    chunk_size: int,
    chunk_overlap: int,
    chunking_strategy: str,
    verbose: bool,  # noqa: FBT001
):
    """Generate summary with a progress indicator, using chunking when needed."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        disable=not verbose,
    ) as progress:
        summarize_task = progress.add_task("Generating summary...", total=None)
        try:
            if len(extracted_text) > chunk_size:
                # Use chunking for large documents
                result = summarizer.summarize_large_document(
                    document,
                    chunk_size=chunk_size,
                    overlap=chunk_overlap,
                    chunking_strategy=chunking_strategy,
                )
            else:
                result = summarizer.summarize_document(document)
        except HlprError:
            # Let domain-specific errors propagate so the outer handler can
            # map them to the appropriate exit codes.
            raise
        except Exception as e:
            err_msg = f"Failed to generate summary: {e}"
            desc = err_msg
            progress.update(summarize_task, completed=True, description=desc)
            console.print(f"[red]Error:[/red] {err_msg}")
            raise typer.Exit(5) from e
        else:
            desc = "Summary generated successfully"
            progress.update(summarize_task, completed=True, description=desc)
            return result


def _parse_meeting_file(file_path: str) -> tuple[str, list[str], list[str]]:
    """Parse meeting file and extract overview, key points, and action items."""
    path = Path(file_path)
    text = path.read_text(encoding="utf-8", errors="ignore")

    overview = text.split("\n", 1)[0].strip() or "Meeting overview"
    key_points = []
    if "action" in text.lower():
        key_points.append("Identified action items")
    if "discuss" in text.lower():
        key_points.append("Discussion points noted")

    # Identify action items: explicit markers or imperative/project TODO lines
    action_items = []
    for line in text.splitlines():
        low = line.lower()
        if any(k in low for k in ["action:", "todo:", "- [ ]", "* [ ]"]) or (
            any(k in low for k in [" will ", " needs to ", " should ", " to "])
            and len(line.strip()) > 5
        ):
            action_items.append(line.strip())

    return overview, key_points, action_items


def _display_meeting_summary(
    overview: str,
    key_points: list[str],
    action_items: list[str],
    output_format: str,
    participants: list[str],
) -> None:
    """Display meeting summary in the specified format."""
    if output_format == "json":
        console.print_json(
            data={
                "overview": overview,
                "key_points": key_points,
                "action_items": action_items,
                "participants": participants,
            },
        )
    else:
    # Provide human-friendly headers: Summary and Overview
        console.print("Summary")
        console.print(overview)
        console.print("\nOverview")
        console.print(overview)
        console.print("\nParticipants")
        if participants:
            for p in participants:
                console.print(f"- {p}")
        else:
            console.print("- None detected")
        console.print("\nKey Points")
        for point in key_points:
            console.print(f"• {point}")
        console.print("\nAction Items")
        if action_items:
            for item in action_items:
                console.print(f"- {item}")
        else:
            console.print("- None detected")


@app.command("meeting")
def summarize_meeting(  # noqa: PLR0913
    file_path: str = typer.Argument(..., help="Path to meeting notes (txt|md)"),
    output_format: str = typer.Option("rich", "--format", help="[txt|md|json|rich]"),
    title: str | None = typer.Option(None, "--title", help="Optional meeting title"),
    date: str | None = typer.Option(None, "--date", help="Optional meeting date"),
    provider: str = typer.Option("local", "--provider", help="AI provider to use"),
    *,
    save: bool = typer.Option(
        default=False,
        help="Save summary to file",
    ),
    output: str | None = typer.Option(None, "--output", help="Output file path"),
) -> None:
    """Summarize meeting notes from a text or markdown file.

    Supports optional title/date metadata, selecting provider, and saving
    the output as JSON when requested.
    """
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        console.print(f"[red]Error:[/red] File not found: {file_path}")
        raise typer.Exit(1)

    if path.suffix.lower() not in {".txt", ".md"}:
        console.print("[red]Error:[/red] Unsupported file format. Use .txt or .md")
        raise typer.Exit(2)

    try:
        overview, key_points, action_items = _parse_meeting_file(file_path)

        # Extract participants (look for 'attendees' or 'present' lines)
        participants = []
        text = path.read_text(encoding="utf-8", errors="ignore")
        for line in text.splitlines():
            low = line.lower()
            if low.startswith(("attendees:", "present:")):
                # Split by commas and parentheses
                parts = line.split(":", 1)[1]
                parts = parts.replace("(", "").replace(")", "")
                participants = [
                    p.strip() for p in parts.split(",") if p.strip()
                ]
                break

        # Include provided metadata into the overview when present
        if title:
            overview = f"{title}\n\n{overview}"
        if date:
            overview = f"{overview}\n\nDate: {date}"

        # If saving as JSON requested, write structured output
        if save and output_format == "json":
            out_path = (
                Path(output)
                if output
                else _determine_output_path(Path(file_path), "json", None)
            )
            out_data = {
                "summary": overview,
                "participants": participants,
                "provider": provider,
                "key_points": key_points,
                "action_items": action_items,
            }
            out_path.write_text(json.dumps(out_data, indent=2), encoding="utf-8")
            console.print(f"[green]Summary saved to:[/green] {out_path}")
            return

        # Otherwise display to console
        _display_meeting_summary(
            overview,
            key_points,
            action_items,
            output_format,
            participants,
        )

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise typer.Exit(4) from e
