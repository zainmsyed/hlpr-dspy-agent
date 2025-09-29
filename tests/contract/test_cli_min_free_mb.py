import shutil

from typer.testing import CliRunner


def test_cli_min_free_mb_blocks_save(tmp_path, monkeypatch):
    """When free space is below the requested --min-free-mb, the CLI should exit with code 7."""
    sample = tmp_path / "sample.md"
    sample.write_text("# Title\n\nBody text")

    # Simulate low free bytes: 5 MiB free
    class FakeDiskUsage:
        total = 100
        used = 95
        free = 5 * 1024 * 1024

    monkeypatch.setattr(shutil, "disk_usage", lambda _: FakeDiskUsage)

    runner = CliRunner()
    result = runner.invoke(
        __import__("hlpr.cli.summarize", fromlist=["app"]).app,
        ["document", str(sample), "--save", "--min-free-mb", "10"],
    )

    # Typer maps StorageError to exit code 7
    assert result.exit_code == 7
    assert "Storage error" in result.output or "Insufficient disk space" in result.output
