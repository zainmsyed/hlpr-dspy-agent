"""Summarize command for hlpr CLI."""

import json
import time
from pathlib import Path
from typing import Optional

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
def summarize_document(
    file_path: str = typer.Argument(..., help="Path to the document file to summarize"),
    provider: str = typer.Option("local", "--provider", help="AI provider to use [local|openai|anthropic]"),
    save: bool = typer.Option(False, "--save", help="Save summary to file"),
    format: str = typer.Option("rich", "--format", help="Output format [txt|md|json|rich]"),
    output: Optional[str] = typer.Option(None, "--output", help="Output file path"),
    chunk_size: int = typer.Option(8192, "--chunk-size", help="Chunk size for large documents"),
    chunk_overlap: int = typer.Option(256, "--chunk-overlap", help="Overlap between chunks"),
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose output"),
):
    """Summarize a document (PDF, DOCX, TXT, MD)."""
    try:
        # Validate file exists
        path = Path(file_path)
        if not path.exists():
            console.print(f"[red]Error:[/red] File not found: {file_path}")
            raise typer.Exit(1)

        if not path.is_file():
            console.print(f"[red]Error:[/red] Path is not a file: {file_path}")
            raise typer.Exit(1)

        # Show progress for parsing
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=not verbose,
        ) as progress:
            parse_task = progress.add_task("Parsing document...", total=None)

            # Parse document
            try:
                extracted_text = DocumentParser.parse_file(file_path)
                progress.update(parse_task, completed=True, description="Document parsed successfully")
            except ValueError as e:
                # Distinguish unsupported format vs general parsing failure
                msg = str(e).lower()
                if "unsupported" in msg or "unsupported file format" in msg:
                    progress.update(parse_task, completed=True, description=f"Unsupported format: {e}")
                    console.print(f"[red]Error:[/red] Unsupported file format: {e}")
                    raise typer.Exit(2)
                else:
                    progress.update(parse_task, completed=True, description=f"Failed to parse document: {e}")
                    console.print(f"[red]Error:[/red] Failed to parse document: {e}")
                    raise typer.Exit(6)
            except Exception as e:
                progress.update(parse_task, completed=True, description=f"Failed to parse document: {e}")
                console.print(f"[red]Error:[/red] Failed to parse document: {e}")
                raise typer.Exit(6)

            # Create document model
            document = Document.from_file(file_path)
            document.extracted_text = extracted_text

            # Initialize summarizer
            summarizer = DocumentSummarizer(provider=provider)

            # Summarize document
            summarize_task = progress.add_task("Generating summary...", total=None)

            try:
                if len(extracted_text) > chunk_size:
                    # Use chunking for large documents
                    result = summarizer.summarize_large_document(
                        document, chunk_size=chunk_size, overlap=chunk_overlap
                    )
                else:
                    result = summarizer.summarize_document(document)

                progress.update(summarize_task, completed=True, description="Summary generated successfully")

            except Exception as e:
                progress.update(summarize_task, completed=True, description=f"Failed to generate summary: {e}")
                console.print(f"[red]Error:[/red] Failed to generate summary: {e}")
                raise typer.Exit(5)

        # Display results
        _display_summary(document, result, format)

        # Save to file if requested
        if save:
            output_path = _save_summary(document, result, format, output)
            console.print(f"\n[green]Summary saved to:[/green] {output_path}")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise typer.Exit(4)


def _display_summary(document: Document, result, format: str):
    """Display the summary results in the specified format."""
    if format == "rich":
        # Rich terminal display
        title = f"Document Summary: {Path(document.path).name}"
        summary_panel = Panel(
            result.summary,
            title="[bold blue]Summary[/bold blue]",
            border_style="blue",
        )
        console.print(summary_panel)

        if result.key_points:
            key_points_text = "\n".join(f"• {point}" for point in result.key_points)
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
        metadata.append(f"Provider: {getattr(result, 'provider', 'unknown')}")

        metadata_panel = Panel(
            metadata,
            title="[bold yellow]Metadata[/bold yellow]",
            border_style="yellow",
        )
        console.print(metadata_panel)

    elif format == "json":
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

    elif format == "txt":
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

    elif format == "md":
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


def _save_summary(document: Document, result, format: str, output_path: Optional[str]) -> str:
    """Save the summary to a file."""
    if output_path:
        save_path = Path(output_path)
    else:
        # Auto-generate output path
        doc_name = Path(document.path).stem
        if format == "json":
            save_path = Path(f"{doc_name}_summary.json")
        elif format == "md":
            save_path = Path(f"{doc_name}_summary.md")
        else:
            save_path = Path(f"{doc_name}_summary.txt")

    # Ensure we don't overwrite without warning
    if save_path.exists():
        console.print(f"[yellow]Warning:[/yellow] Overwriting existing file: {save_path}")

    # Generate content based on format
    if format == "json":
        output_data = {
            "file": str(Path(document.path).name),
            "format": document.format.value,
            "size_bytes": document.size_bytes,
            "summary": result.summary,
            "key_points": result.key_points,
            "processing_time_ms": result.processing_time_ms,
        }
        content = json.dumps(output_data, indent=2)

    elif format == "md":
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

    else:  # txt or rich
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

    # Write to file
    with save_path.open("w", encoding="utf-8") as f:
        f.write(content)

    return str(save_path)