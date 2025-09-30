"""Contract tests for CLI save behavior (specs/006-title-interactive-save/contracts/cli-behavior.md)"""

from typer.testing import CliRunner

from hlpr.cli.main import app


def test_cli_save_behavior_smoke():
    # Placeholder contract test: ensure CLI entrypoint runs without error
    runner = CliRunner()
    result = runner.invoke(app, ["summarize", "document", "--help"])  # smoke command
    assert result.exit_code == 0
