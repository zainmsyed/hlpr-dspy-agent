from __future__ import annotations

from typing import List, Optional

import typer

from rich.console import Console

from hlpr.cli.batch import BatchOptions, BatchProcessor
from hlpr.cli.models import FileSelection, OutputFormat
from hlpr.cli.renderers import RichRenderer, JsonRenderer, MarkdownRenderer, PlainTextRenderer

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
    def summarize_fn(file_sel: FileSelection):
        # Placeholder: real summarization will call providers/summarizer
        from hlpr.cli.models import ProcessingResult

        return ProcessingResult(file=file_sel, summary=f"(stub) summary for {file_sel.path}")

    results = processor.process_files(selections, summarize_fn)

    for r in results:
        # renderer.render returns a string; print it so the CLI shows output
        out = renderer.render(r)
        print(out)


def main():
    app()


if __name__ == "__main__":
    main()
