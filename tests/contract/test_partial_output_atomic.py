import json

from typer.testing import CliRunner

from hlpr.cli.main import app

runner = CliRunner()


def test_partial_output_atomic_write(tmp_path, monkeypatch):
    # Prepare one file and an output path
    f = tmp_path / "doc.txt"
    f.write_text("hello world")
    out = tmp_path / "partial.json"

    # Monkeypatch BatchProcessor to simulate an interrupted run
    from hlpr.cli.batch import BatchProcessor

    class DummyProcessor(BatchProcessor):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.interrupted = True

    def process_files(self, *_a, **_k):
        # Return a single ProcessingResult-like dict via renderer path
        from hlpr.cli.models import FileSelection, ProcessingResult

        pr = ProcessingResult(file=FileSelection(path=str(f)))
        pr.summary = "partial"
        return [pr]

    monkeypatch.setattr("hlpr.cli.summarize.BatchProcessor", DummyProcessor)

    result = runner.invoke(
        app,
        [
            "summarize",
            "documents",
            "--provider",
            "local",
            "--format",
            "json",
            "--partial-output",
            str(out),
            str(f),
        ],
    )

    assert result.exit_code == 0
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "data" in data
    assert isinstance(data["data"], list)
