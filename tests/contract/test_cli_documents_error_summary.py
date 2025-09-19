from pathlib import Path
from typer.testing import CliRunner
from hlpr.cli.main import app

runner = CliRunner()


def test_documents_error_summary(tmp_path):
    # Create three files; one will be made unreadable to simulate a parser error
    good1 = tmp_path / "good1.txt"
    good2 = tmp_path / "good2.txt"
    bad = tmp_path / "bad.txt"

    good1.write_text("This is a short document.")
    good2.write_text("Another valid document.")
    bad.write_text("This file will be made unreadable.")

    # Make the bad file unreadable to trigger a parse error (permission error)
    bad.chmod(0)

    try:
        result = runner.invoke(
            app,
            [
                "summarize",
                "documents",
                "--provider",
                "local",
                "--format",
                "txt",
                str(good1),
                str(bad),
                str(good2),
            ],
        )

        # CLI should complete (best-effort) and print a warning about failures
        assert result.exit_code == 0
        output = result.output
        assert "Warning" in output or "failed to process" in output
        # Should mention the bad file
        assert "bad.txt" in output
        # Should include the rerun hint for the failed file
        assert "Hint: run `hlpr summarize document" in output
    finally:
        # Restore permissions so tmpdir can be cleaned up
        try:
            bad.chmod(0o644)
        except Exception:
            pass
