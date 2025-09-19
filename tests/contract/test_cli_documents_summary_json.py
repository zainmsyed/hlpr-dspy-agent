import json

from typer.testing import CliRunner

from hlpr.cli.main import app

runner = CliRunner()


def test_documents_summary_json(tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("doc 1")
    f2.write_text("doc 2")

    out = tmp_path / "summary.json"

    result = runner.invoke(
        app,
        [
            "summarize",
            "documents",
            "--provider",
            "local",
            "--format",
            "json",
            "--summary-json",
            str(out),
            str(f1),
            str(f2),
        ],
    )

    assert result.exit_code == 0
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "summary" in data
    assert data["summary"]["total_files"] == 2
    assert isinstance(data["files"], list)
    assert len(data["files"]) == 2
    paths = {p["path"] for p in data["files"]}
    assert str(f1) in paths and str(f2) in paths
