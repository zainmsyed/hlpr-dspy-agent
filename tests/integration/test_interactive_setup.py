from pathlib import Path

from hlpr.cli.config import setup_config
from hlpr.config.models import ConfigurationPaths


def test_interactive_setup_creates_files(tmp_path, monkeypatch):
    """Ensure config files are created when setup runs (non-interactive call).

    Interactive prompt coverage is handled elsewhere; for CI we call the
    setup function with non_interactive=True to avoid flaky prompt handling.
    """
    monkeypatch.setenv("HOME", str(tmp_path))

    paths = ConfigurationPaths.default()
    if paths.config_dir.exists():
        # Clean any previous
        for p in paths.config_dir.iterdir():
            if p.is_file():
                p.unlink()
    # Call the setup function in non-interactive mode; it will raise click.Exit on success
    try:
        setup_config(non_interactive=True)
    except Exception:
        # typer raises click.exceptions.Exit; ignore for this test
        pass

    config_dir = tmp_path / ".hlpr"
    assert config_dir.exists()
    assert (config_dir / "config.yaml").exists()
    assert (config_dir / ".env").exists()
