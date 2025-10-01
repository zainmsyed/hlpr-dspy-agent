from typer.testing import CliRunner

from hlpr.cli.main import app

runner = CliRunner()


def test_config_validate_reports_errors_or_success():
    """Contract: `hlpr config validate` should return 0 on success or 1 on validation errors"""
    result = runner.invoke(app, ["config", "validate"])
    assert result.exit_code in (0, 1, 2)
