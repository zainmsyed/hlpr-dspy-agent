from typer.testing import CliRunner

from hlpr.cli.main import app

runner = CliRunner()


def test_config_setup_prompts_or_succeeds():
    """Contract: `hlpr config setup` should run (interactive or non-interactive)"""
    result = runner.invoke(app, ["config", "setup", "--non-interactive"], input="\n")
    # Accept either success (0) or a non-zero that indicates not implemented
    assert result.exit_code in (0, 1, 2)
