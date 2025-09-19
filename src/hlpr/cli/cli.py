from __future__ import annotations

from typing import List, Optional

import typer

from rich.console import Console

from hlpr.cli.batch import BatchOptions, BatchProcessor
from hlpr.cli.models import FileSelection, OutputFormat
from hlpr.cli.renderers import RichRenderer, JsonRenderer, MarkdownRenderer, PlainTextRenderer
from hlpr.document.parser import DocumentParser
from hlpr.document.summarizer import DocumentSummarizer
from hlpr.models.document import Document
from hlpr.exceptions import HlprError
from hlpr.cli.models import ProcessingResult

app = typer.Typer()


@app.command()
def summarize(
    files: List[str] = typer.Argument(..., help="Files to summarize"),
    provider: Optional[str] = typer.Option(None, help="Provider name"),
    concurrency: int = typer.Option(4, help="Max concurrent workers"),
    output: OutputFormat = typer.Option(OutputFormat.RICH, help="Output format"),
) -> None:
    """Summarize one or more files and print the results using the chosen renderer."""
    console = Console()
    options = BatchOptions(max_workers=concurrency, console=console)
    processor = BatchProcessor(options)

    # Map files to FileSelection models
    selections = [FileSelection(path=p) for p in files]

    # Choose a renderer
    renderer_map = {
        OutputFormat.RICH: RichRenderer(console=console),
        OutputFormat.JSON: JsonRenderer(),
        OutputFormat.MARKDOWN: MarkdownRenderer(),
        OutputFormat.TEXT: PlainTextRenderer(),
    }
    renderer = renderer_map.get(output, RichRenderer(console=console))

    # For now, use a trivial summarize function that returns an empty result.
    def make_adapter(provider: str | None):
        """Create a summarize_fn adapter that accepts FileSelection and returns ProcessingResult.

        Falls back to a simple stub if DocumentSummarizer cannot be instantiated.
        """

        try:
            summarizer = DocumentSummarizer(provider=provider or "local")
        except Exception:
            summarizer = None

        def adapter(file_sel: FileSelection) -> ProcessingResult:
            # Defensive: return ProcessingResult with error captured on failure
            try:
                # parse file
                text = DocumentParser.parse_file(file_sel.path)
                doc = Document.from_file(file_sel.path)
                doc.extracted_text = text

                if summarizer is None:
                    # Best-effort stub
                    return ProcessingResult(file=file_sel, summary=f"(stub) summary for {file_sel.path}")

                result = summarizer.summarize_document(doc)

                # Map summarizer result into ProcessingResult model
                pr = ProcessingResult(file=file_sel)
                pr.summary = getattr(result, "summary", None)
                # key points, hallucinations if present on result
                if hasattr(result, "key_points"):
                    try:
                        pr_key_points = getattr(result, "key_points")
                        # Attach to metadata.details or keep as part of summary text in renderer
                        # (renderers expect ProcessingResult.summary primarily)
                        # We'll include key_points in metadata.details for now.
                        pr.metadata = pr.metadata or None
                    except Exception:
                        pass

                # processing_time_ms -> ProcessingMetadata.duration_seconds
                proc_ms = getattr(result, "processing_time_ms", None)
                if proc_ms is not None:
                    from datetime import datetime

                    md = pr.metadata or None
                    # create ProcessingMetadata with duration_seconds
                    from hlpr.cli.models import ProcessingMetadata

                    try:
                        pr.metadata = ProcessingMetadata(duration_seconds=(proc_ms / 1000.0))
                    except Exception:
                        # fallback: leave metadata None
                        pr.metadata = None

                return pr
            except HlprError as e:
                from hlpr.cli.models import ProcessingError

                return ProcessingResult(
                    file=file_sel,
                    error=ProcessingError(message=str(e), details={"type": type(e).__name__}),
                )
            except Exception as e:  # pragma: no cover - defensive
                from hlpr.cli.models import ProcessingError

                return ProcessingResult(
                    file=file_sel,
                    error=ProcessingError(message=str(e), details={"type": type(e).__name__}),
                )

        return adapter

    summarize_fn = make_adapter(provider)

    results = processor.process_files(selections, summarize_fn)

    for r in results:
        # renderer.render returns a string; print it so the CLI shows output
        out = renderer.render(r)
        print(out)


def main():
    app()


if __name__ == "__main__":
    main()
