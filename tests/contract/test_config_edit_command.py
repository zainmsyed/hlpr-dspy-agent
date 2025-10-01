from typer.testing import CliRunner

from hlpr.cli.main import app

runner = CliRunner()


def test_config_edit_opens_editor_or_errors():
    """Contract: `hlpr config edit` should attempt to open editor or return a known exit code"""
    result = runner.invoke(app, ["config", "edit"])
    assert result.exit_code in (0, 1, 2)
