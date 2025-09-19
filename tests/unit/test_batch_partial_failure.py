from rich.console import Console

from hlpr.cli.batch import BatchOptions, BatchProcessor
from hlpr.cli.models import FileSelection, ProcessingError, ProcessingResult


def test_batch_partial_failure():
    console = Console()
    options = BatchOptions(max_workers=2, console=console)
    bp = BatchProcessor(options)

    files = [FileSelection(path="a.txt"), FileSelection(path="b.txt")]

    # Summarize function: raise for a.txt, return success for b.txt
    def summarize_fn(file_sel):
        if file_sel.path == "a.txt":
            raise RuntimeError("simulated failure")
        pr = ProcessingResult(file=file_sel)
        pr.summary = "ok"
        return pr

    results = bp.process_files(files, summarize_fn)

    # We expect two results; one with error, one with summary
    assert len(results) == 2
    errors = [r for r in results if r.error]
    successes = [r for r in results if not r.error]

    assert len(errors) == 1
    assert isinstance(errors[0].error, ProcessingError)
    assert "simulated failure" in errors[0].error.message
    assert len(successes) == 1
    assert successes[0].summary == "ok"
