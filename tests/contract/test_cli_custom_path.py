from typer.testing import CliRunner


def test_cli_respects_custom_output_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    doc = tmp_path / "test_document.txt"
    doc.write_text("some content")
    custom = tmp_path / "custom_summary.txt"

    runner = CliRunner()
    from hlpr.cli.main import app as main_app

    res = runner.invoke(
        main_app, ["summarize", "document", str(doc), "--save", "--output", str(custom)]
    )
    assert res.exit_code == 0, res.output
    assert custom.exists(), "Custom output file should be created when using --output"
