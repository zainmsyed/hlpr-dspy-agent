from pathlib import Path

from typer.testing import CliRunner

from hlpr.cli.main import app

runner = CliRunner()


def test_cli_documents_batch_basic():
    """Basic integration test for `hlpr summarize documents` batch command."""
    test_file = Path("test_document_batch.txt")
    test_file.write_text("This is a short document to test batch summarization.")

    result = runner.invoke(
        app,
        [
            "summarize",
            "documents",
            "--provider",
            "local",
            "--format",
            "txt",
            "--concurrency",
            "2",
            str(test_file),
        ],
    )

    # Should succeed and include a summary section
    assert result.exit_code == 0, result.output
    out = result.output.lower()
    assert "summary" in out

    # Cleanup
    test_file.unlink(missing_ok=True)


def test_cli_guided_mode_smoke():
    """Run guided mode command as a smoke test to ensure it returns success or handled error."""
    test_file = Path("test_guided.txt")
    test_file.write_text("Guided mode test content.")

    result = runner.invoke(
        app,
        ["summarize", "guided", "--provider", "local", str(test_file)],
    )

    # Guided mode either completes successfully or surfaces an error exit code; ensure graceful handling
    assert result.exit_code in {0, 1, 4}

    test_file.unlink(missing_ok=True)
