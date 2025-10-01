from typer.testing import CliRunner

from hlpr.cli.main import app

runner = CliRunner()


def test_first_run_setup_creates_files(tmp_path, monkeypatch):
    # Point default path to tmp home
    monkeypatch.setenv("HOME", str(tmp_path))

    result = runner.invoke(app, ["config", "setup", "--non-interactive"])
    assert result.exit_code == 0

    config_dir = tmp_path / ".hlpr"
    assert config_dir.exists()
    assert (config_dir / "config.yaml").exists()
    assert (config_dir / ".env").exists()
