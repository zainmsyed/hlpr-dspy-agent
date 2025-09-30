from typer.testing import CliRunner


def test_cli_creates_organized_storage(tmp_path, monkeypatch):
    # Arrange: create a small document and run CLI in tmpdir
    cwd = tmp_path
    doc = cwd / "test_document.txt"
    doc.write_text("This is a test document for organized storage")
    monkeypatch.chdir(cwd)

    runner = CliRunner()
    from hlpr.cli.main import app as main_app

    # Act: run the CLI summarize document command with --save (default format should produce .md)
    res = runner.invoke(main_app, ["summarize", "document", str(doc), "--save"])

    # Assert: command succeeded and organized folder exists with expected file
    assert res.exit_code == 0, res.output
    summaries_dir = cwd / "hlpr" / "summaries" / "documents"
    assert summaries_dir.exists(), (
        "Organized summaries directory should exist after CLI save"
    )
    # Check for the generated summary file
    expected = summaries_dir / "test_document_summary.md"
    assert expected.exists(), f"Expected summary file at {expected}"
