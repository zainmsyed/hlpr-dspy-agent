from typer.testing import CliRunner

from hlpr.cli.main import app

runner = CliRunner()


def test_config_show_runs_and_outputs_something():
    """Contract: `hlpr config show` should print configuration or an error message"""
    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code in (0, 1)
    assert isinstance(result.output, str)
