from typer.testing import CliRunner


def test_storage_permission_denied(tmp_path, monkeypatch):
    # Simulate permission denied scenario - after implementation this should be handled
    protected = tmp_path / "protected"
    protected.mkdir()

    # Create a document in tmp_path (not inside protected) so we can call CLI
    doc = tmp_path / "doc.txt"
    doc.write_text("data")

    # Force the application to use the protected directory as the organized base
    from hlpr.models.output_preferences import OutputPreferences

    monkeypatch.setattr(OutputPreferences, "effective_base", lambda _: protected)

    # Make directory unwritable after we've created the doc
    protected.chmod(0o400)

    runner = CliRunner()
    from hlpr.cli.main import app as main_app

    # Run CLI with save; expect non-zero exit or that summaries are not created in protected
    res = runner.invoke(main_app, ["summarize", "document", str(doc), "--save"])
    summaries_dir = protected / "hlpr" / "summaries" / "documents"
    assert res.exit_code != 0 or not summaries_dir.exists()
