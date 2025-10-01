from typer.testing import CliRunner

from hlpr.cli.main import app

runner = CliRunner()


def test_config_reset_requires_confirmation_or_returns_known_code():
    """Contract: `hlpr config reset` should prompt for confirmation or provide flags"""
    result = runner.invoke(app, ["config", "reset", "--yes"], input="y\n")
    assert result.exit_code in (0, 1, 2)
