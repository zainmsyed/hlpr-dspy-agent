"""Summarize command for hlpr CLI."""

import contextlib
import json
import logging
import sys
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

from hlpr.cli.batch import BatchOptions, BatchProcessor
from hlpr.cli.interactive import InteractiveSession
from hlpr.cli.models import (
    FileSelection,
    OutputFormat,
    ProcessingError,
    ProcessingMetadata,
    ProcessingResult,
)
from hlpr.cli.prompt_providers import RichTyperPromptProvider
from hlpr.cli.renderers import (
    JsonRenderer,
    MarkdownRenderer,
    PlainTextRenderer,
    RichRenderer,
)
from hlpr.cli.rich_display import RichDisplay
from hlpr.config import CONFIG
from hlpr.document.parser import DocumentParser
from hlpr.document.summarizer import DocumentSummarizer
from hlpr.exceptions import (
    ConfigurationError,
    DocumentProcessingError,
    HlprError,
    SummarizationError,
)
from hlpr.io.atomic import atomic_write_text
from hlpr.logging_utils import build_extra, build_safe_extra, new_context
from hlpr.models.document import Document
from hlpr.models.saved_commands import SavedCommands

logger = logging.getLogger(__name__)

# Create typer app for summarize commands
app = typer.Typer(help="Document summarization commands")

# Console for rich output
console = Console()


@app.command("document")
def summarize_document(
    file_path: str = typer.Argument(..., help="Path to the document file to summarize"),
    provider: str = typer.Option(
        "local",
        "--provider",
        help=(
            "AI provider to use [local|openai|anthropic|groq|together]"
        ),
    ),
        save: bool = typer.Option(
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
    verbose: bool = typer.Option(
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
    no_fallback: bool = typer.Option(
        default=False,
        help="Disable fallback to local summarizer on DSPy failure",
    ),
    verify_hallucinations: bool = typer.Option(
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
        log_ctx = new_context()
        start_extra = {"provider": provider}
        if CONFIG.include_file_paths:
            start_extra["file"] = str(path)

        logger.info(
            "CLI document summarization started",
            extra=build_safe_extra(log_ctx, **start_extra),
        )
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
        complete_extra = {"provider": provider}
        if CONFIG.include_file_paths:
            complete_extra["file"] = str(path)
        if CONFIG.performance_logging:
            complete_extra["processing_time_ms"] = (
                getattr(result, "processing_time_ms", None)
            )

        logger.info(
            "CLI document summarization completed",
            extra=build_safe_extra(log_ctx, **complete_extra),
        )

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
        logger.info(
            "CLI domain error",
            extra=build_extra(log_ctx, error=str(he), error_type=type(he).__name__),
        )
        raise typer.Exit(3) from he
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        logger.exception(
            "Unexpected CLI error",
            extra=build_extra(log_ctx, error=str(e)),
        )
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
        proc_ms = getattr(result, "processing_time_ms", None)
        proc_seconds_str = f"{(proc_ms / 1000.0):.2f} seconds" if proc_ms is not None else "unknown"
        metadata.append(f"Processing time: {proc_seconds_str}\n")
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
        proc_ms = getattr(result, "processing_time_ms", None)
        output_data = {
            "file": str(Path(document.path).name),
            "format": document.format.value,
            "size_bytes": document.size_bytes,
            "summary": result.summary,
            "key_points": result.key_points,
            "hallucinations": getattr(result, "hallucinations", []),
            "processing_time_ms": proc_ms,
            "processing_time_seconds": (proc_ms / 1000.0) if proc_ms is not None else None,
            "provider": getattr(result, "provider", None),
        }
        console.print_json(data=output_data)

    elif output_format == "txt":
        # Plain text output
        console.print(f"Document: {Path(document.path).name}")
        console.print(f"Format: {document.format.value.upper()}")
        console.print(f"Size: {document.size_bytes:,} bytes")
        proc_ms = getattr(result, "processing_time_ms", None)
        proc_seconds_str = f"{(proc_ms / 1000.0):.2f} seconds" if proc_ms is not None else "unknown"
        console.print(f"Processing time: {proc_seconds_str}")
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
        proc_ms = getattr(result, "processing_time_ms", None)
        proc_seconds_str = f"{(proc_ms / 1000.0):.2f} seconds" if proc_ms is not None else "unknown"
        console.print(f"- **Processing time**: {proc_seconds_str}")
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
        proc_ms = getattr(result, "processing_time_ms", None)
        proc_seconds_str = f"{(proc_ms / 1000.0):.2f} seconds" if proc_ms is not None else "unknown"
        content += f"- **Processing time**: {proc_seconds_str}\n\n"
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
    proc_ms = getattr(result, "processing_time_ms", None)
    proc_seconds_str = f"{(proc_ms / 1000.0):.2f} seconds" if proc_ms is not None else "unknown"
    content += f"Processing time: {proc_seconds_str}\n\n"
    content += "SUMMARY:\n"
    content += f"{result.summary}\n\n"
    if result.key_points:
        content += "KEY POINTS:\n"
        for point in result.key_points:
            content += f"• {point}\n"
    return content


def _parse_with_progress(file_path: str, verbose: bool) -> tuple[Document, str]:
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


def _summarize_with_progress(
    summarizer: DocumentSummarizer,
    document: Document,
    extracted_text: str,
    chunk_size: int,
    chunk_overlap: int,
    chunking_strategy: str,
    verbose: bool,
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
def summarize_meeting(
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


@app.command("guided")
def summarize_guided(
    file_path: str = typer.Argument(..., help="Path to the document file to summarize"),
    provider: str = typer.Option("local", "--provider", help="AI provider to use"),
    output_format: str = typer.Option("rich", "--format", help="Output format [txt|md|json|rich]"),
    simulate_work: bool = typer.Option(False, help="Simulate work during the guided flow"),
    execute: bool = typer.Option(True, "--execute/--no-execute", help="Run parse+summarization after prompts (default: interactive execute)"),
) -> None:
    """Run the guided interactive summarization flow.

    This command delegates to `InteractiveSession.run_with_phases` which
    provides a phase-aware progress UI used by tests and integration.
    """
    display = RichDisplay()
    # Use interactive Typer/Rich prompts when running in a TTY, otherwise
    # fall back to defaults to allow non-interactive runs (tests/CI).
    prompt_provider = None
    if sys.stdin.isatty():
        prompt_provider = RichTyperPromptProvider()
    session = InteractiveSession(display=display, prompt_provider=prompt_provider)

    try:
        # Interactive default: prefer the high-level guided workflow which
        # collects options (basic + advanced), runs processing, and generates
        # command templates. This keeps guided mode interactive by default.
        if execute:
            # Collect options interactively (basic + advanced) and then run
            # the real parse + summarization path. We avoid relying on the
            # simulation-only run_with_phases here so guided mode actually
            # performs processing when the user requests execution.
            base_opts = session.collect_basic_options({"provider": provider, "format": output_format})
            opts = session.collect_advanced_options(base_opts, {})

            # Convert ProcessingOptions to plain dict for compatibility
            opts_dict = opts.model_dump() if hasattr(opts, "model_dump") else dict(opts)
            if "output_format" not in opts_dict and "format" in opts_dict:
                opts_dict["output_format"] = opts_dict.get("format")

            # Validate file existence before heavy work
            path = Path(file_path)
            if not path.exists() or not path.is_file():
                display.show_error_panel("Validation Error", f"File not found or invalid: {file_path}")
                raise typer.Exit(1)

            # Parse the document with progress
            document, extracted_text = _parse_with_progress(file_path, verbose=False)

            # Build summarizer using options collected
            timeout_val = CONFIG.default_timeout
            summarizer = DocumentSummarizer(
                provider=opts_dict.get("provider", "local"),
                model=opts_dict.get("model", "gemma3:latest"),
                temperature=opts_dict.get("temperature", 0.3),
                timeout=timeout_val,
            )

            # Run summarization
            result = _summarize_with_progress(
                summarizer,
                document,
                extracted_text,
                opts_dict.get("chunk_size", 8192),
                opts_dict.get("chunk_overlap", 256),
                opts_dict.get("chunking_strategy", "sentence"),
                verbose=False,
            )

            # Display summary using requested format
            _display_summary(document, result, opts_dict.get("output_format", "rich"))

            # Persist command template for reproducibility (non-fatal)
            try:
                template = session.generate_command_template(opts)
                saver = session.command_saver or SavedCommands()
                try:
                    saver.save_command(template)
                except Exception:
                    logger.warning("Failed to persist command template")
                try:
                    session.display_command_template(template)
                except Exception:
                    logger.warning("Failed to display command template")
            except Exception:
                logger.warning("Command template generation failed")

            # We've completed the execute path; return to avoid running
            # the legacy non-execute simulation path below. When this
            # handler is invoked with execute=True we should not fall
            # through to `run_with_phases` which expects different
            # option types and is intended only for the simulated path.
            return

        # Non-execute (--no-execute) legacy path: simulate phases using the
        # lower-level run_with_phases to preserve test behavior and allow
        # non-interactive demonstrations.
        options = {
            "simulate_work": simulate_work,
            "provider": provider,
            "output_format": output_format,
        }
        res = session.run_with_phases(file_path, options)
        if res.get("status") == "error":
            display.show_error_panel("Guided Mode Error", res.get("message", "Unknown error"))
            raise typer.Exit(1)
        display.show_panel("Success", "Guided mode completed successfully")
        return

    except typer.Exit:
        raise
    except HlprError as he:
        # Reuse upstream HlprError handling for better exit codes
        if isinstance(he, DocumentProcessingError):
            display.show_error_panel("Document error", str(he))
            raise typer.Exit(6) from he
        if isinstance(he, SummarizationError):
            display.show_error_panel("Summarization error", str(he))
            raise typer.Exit(5) from he
        if isinstance(he, ConfigurationError):
            display.show_error_panel("Configuration error", str(he))
            raise typer.Exit(2) from he
        display.show_error_panel("Error", str(he))
        raise typer.Exit(3) from he
    except Exception as e:
        display.show_error_panel("Unexpected Error", str(e))
        raise typer.Exit(4) from e


@app.command("documents")
def summarize_documents(
    files: list[str] = typer.Argument(..., help="Files to summarize"),
    provider: str = typer.Option("local", "--provider", help="AI provider to use"),
    format: OutputFormat = typer.Option(OutputFormat.RICH, "--format", help="Output format"),
    concurrency: int = typer.Option(4, "--concurrency", help="Max concurrent workers"),
    partial_output: str | None = typer.Option(
        None, "--partial-output", help="Path to write partial results JSON if run is interrupted",
    ),
    summary_json: str | None = typer.Option(None, "--summary-json", help="Path to write machine-readable batch summary JSON (omit to print to stdout)"),
) -> None:
    """Summarize multiple documents concurrently.

    This command is the canonical batch entrypoint for installed `hlpr` CLI and
    will parse each file and call the configured summarizer concurrently.
    """
    console = Console()

    # Prepare BatchProcessor
    options = BatchOptions(max_workers=concurrency, console=console)
    processor = BatchProcessor(options)

    # Map input paths to FileSelection (include size when available)
    selections = []
    for p in files:
        try:
            pth = Path(p)
            size = pth.stat().st_size if pth.exists() and pth.is_file() else None
        except OSError:
            # Could not stat file (e.g., permission denied) — treat size as unknown
            size = None
        selections.append(FileSelection(path=p, size_bytes=size))

    # Renderer selection
    renderer_map = {
        OutputFormat.RICH: RichRenderer(console=console),
        OutputFormat.JSON: JsonRenderer(),
        OutputFormat.MARKDOWN: MarkdownRenderer(),
        OutputFormat.TEXT: PlainTextRenderer(),
    }
    renderer = renderer_map.get(format, RichRenderer(console=console))

    def make_adapter(provider_name: str | None):
        try:
            summarizer = DocumentSummarizer(provider=provider_name or "local")
        except Exception:
            summarizer = None

        def adapter(file_sel: FileSelection) -> ProcessingResult:
            try:
                text = DocumentParser.parse_file(file_sel.path)
                doc = Document.from_file(file_sel.path)
                doc.extracted_text = text

                if summarizer is None:
                    return ProcessingResult(file=file_sel, summary=f"(stub) summary for {file_sel.path}")

                result = summarizer.summarize_document(doc)

                pr = ProcessingResult(file=file_sel)
                pr.summary = getattr(result, "summary", None)

                # Build metadata once and populate known fields
                meta = ProcessingMetadata()
                proc_ms = getattr(result, "processing_time_ms", None)
                if proc_ms is not None:
                    meta.duration_seconds = (proc_ms / 1000.0)

                provider_name = getattr(result, "provider", None)
                if provider_name:
                    meta.provider = provider_name

                key_points = getattr(result, "key_points", None)
                if key_points:
                    meta.key_points = key_points

                hallucinations = getattr(result, "hallucinations", None)
                if hallucinations:
                    meta.hallucinations = hallucinations

                # Only attach metadata if any of the fields were set
                if any(
                    [
                        meta.duration_seconds is not None,
                        meta.provider is not None,
                        meta.key_points is not None,
                        meta.hallucinations is not None,
                    ],
                ):
                    pr.metadata = meta

                return pr
            except Exception as e:
                return ProcessingResult(
                    file=file_sel,
                    error=ProcessingError(message=str(e), details={"type": type(e).__name__}),
                )

        return adapter

    summarize_fn = make_adapter(provider)

    results = processor.process_files(selections, summarize_fn)

    for r in results:
        out = renderer.render(r)
        # Renderers return formatted string or console text; print to stdout
        console.print(out)

    # Batch-level error summary for visibility
    error_results = [r for r in results if r.error]
    if error_results:
        console.print(f"\n[yellow]Warning:[/yellow] {len(error_results)} file(s) failed to process")
        # Show up to three example failures with brief diagnostics and a hint
        for er in error_results[:3]:
            # Prefer structured code when available
            code = getattr(er.error, "code", None) or er.error.details.get("type") if er.error.details else None
            msg = (er.error.message or "Unknown error").strip()
            # Truncate long messages for terminal readability
            if len(msg) > 240:
                msg = msg[:237] + "..."
            details = ""
            if er.error.details:
                with contextlib.suppress(Exception):
                    details = f" ({er.error.details})"

            console.print(
                f"  [red]✗[/red] {er.file.path}: {msg}{details} {f'[code={code}]' if code else ''}",
            )
            console.print(f"      Hint: run `hlpr summarize document {er.file.path}` to reproduce")
        if len(error_results) > 3:
            console.print(f"  ... and {len(error_results) - 3} more errors")

    # Persist partial results if the run was interrupted and user requested a path
    if partial_output and getattr(processor, "interrupted", False):
        console.print(f"[yellow]Run interrupted; saving partial results to {partial_output}[/yellow]")
        jr = JsonRenderer()
        # Convert list of ProcessingResult pydantic models to serializable JSON
        json_text = jr.render(results)
        # Write atomically to avoid truncated/corrupt partial files on crash
        try:
            atomic_write_text(partial_output, json_text)
        except OSError:
            # Fallback to best-effort write if atomic helper fails at OS level
            Path(partial_output).write_text(json_text, encoding="utf-8")

    # Machine-readable batch summary (per-file status + counts)
    if summary_json is not None:
        summary = {
            "summary": {
                "total_files": len(results),
                "succeeded": len([r for r in results if not r.error]),
                "failed": len([r for r in results if r.error]),
            },
            "files": [],
        }
        for r in results:
            entry = {
                "path": r.file.path,
                "success": r.error is None,
                "summary": r.summary,
                "metadata": r.metadata.model_dump() if r.metadata else None,
                "error": r.error.model_dump() if r.error else None,
            }
            summary["files"].append(entry)

        # Use raw JSON (not JsonRenderer) for a predictable machine-readable
        # top-level structure that callers expect.

        summary_text = json.dumps(summary, indent=2, ensure_ascii=False)

        # If user passed empty string, print to stdout, else write to path atomically
        if summary_json == "":
            # Print to stdout
            console.print_json(data=summary)
        else:
            try:
                atomic_write_text(summary_json, summary_text)
                console.print(f"[green]Batch summary written to {summary_json}[/green]")
            except OSError:
                # Best-effort fallback when atomic write cannot complete due to OS-level error
                Path(summary_json).write_text(summary_text, encoding="utf-8")

