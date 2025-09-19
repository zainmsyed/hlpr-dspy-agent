from hlpr.cli.batch import BatchOptions, BatchProcessor
from hlpr.cli.models import FileSelection, ProcessingResult


def test_batch_processor_aggregates_results(tmp_path):
    files = [
        FileSelection(path=str(tmp_path / "a.txt")),
        FileSelection(path=str(tmp_path / "b.txt")),
    ]

    def fake_summarize(f):
        # Return a ProcessingResult with a summary mentioning the path
        r = ProcessingResult(file=f)
        r.summary = f"summary for {f.path}"
        return r

    proc = BatchProcessor(BatchOptions(max_workers=2))
    results = proc.process_files(files, fake_summarize)

    assert len(results) == 2
    paths = {r.file.path for r in results}
    assert paths == {files[0].path, files[1].path}
    for r in results:
        assert r.summary is not None
        assert r.summary.startswith("summary for")
