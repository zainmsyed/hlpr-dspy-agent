"""Summarize command for hlpr CLI."""

import json
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

from hlpr.document.parser import DocumentParser
from hlpr.document.summarizer import DocumentSummarizer
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

        # Initialize summarizer
        summarizer = DocumentSummarizer(provider=provider)

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
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise typer.Exit(4) from e


def _display_summary(document: Document, result: Any, output_format: str) -> None:
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

    elif output_format == "json":
        # JSON output
        output_data = {
            "file": str(Path(document.path).name),
            "format": document.format.value,
            "size_bytes": document.size_bytes,
            "summary": result.summary,
            "key_points": result.key_points,
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
        except ValueError as e:
            # Distinguish unsupported format vs general parsing failure
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

    action_items = [
        line.strip()
        for line in text.splitlines()
        if any(k in line.lower() for k in ["action:", "todo:", "- [ ]", "* [ ]"])
    ]

    return overview, key_points, action_items


def _display_meeting_summary(
    overview: str, key_points: list[str], action_items: list[str], output_format: str,
) -> None:
    """Display meeting summary in the specified format."""
    if output_format == "json":
        console.print_json(
            data={
                "overview": overview,
                "key_points": key_points,
                "action_items": action_items,
            },
        )
    else:
        console.print("Overview")
        console.print(overview)
        console.print("\nKey Points")
        for point in key_points:
            console.print(f"• {point}")
        console.print("\nAction Items")
        for item in action_items:
            console.print(f"- {item}")


@app.command("meeting")
def summarize_meeting(
    file_path: str = typer.Argument(..., help="Path to meeting notes (txt|md)"),
    output_format: str = typer.Option("rich", "--format", help="[txt|md|json|rich]"),
) -> None:
    """Summarize meeting notes from a text or markdown file."""
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        console.print(f"[red]Error:[/red] File not found: {file_path}")
        raise typer.Exit(1)

    if path.suffix.lower() not in {".txt", ".md"}:
        console.print("[red]Error:[/red] Unsupported file format. Use .txt or .md")
        raise typer.Exit(2)

    try:
        overview, key_points, action_items = _parse_meeting_file(file_path)
        _display_meeting_summary(overview, key_points, action_items, output_format)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise typer.Exit(4) from e
