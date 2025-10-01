import os
import shutil
from pathlib import Path

import click

from hlpr.cli.config import setup_config
from hlpr.config.models import ConfigurationPaths


def test_setup_writes_templates(tmp_path, monkeypatch):
    # Use a temporary home directory to avoid touching the user's real ~/.hlpr
    monkeypatch.setenv("HOME", str(tmp_path))

    paths = ConfigurationPaths.default()
    # Ensure no pre-existing directory
    if paths.config_dir.exists():
        shutil.rmtree(paths.config_dir)

    # Call the setup function directly in non-interactive mode. It raises Typer's Exit (SystemExit)
    try:
        setup_config(non_interactive=True)
    except click.exceptions.Exit as e:
        # typer raises click.exceptions.Exit; ensure it signalled success
        assert getattr(e, "exit_code", 0) == 0

    # Files should exist
    assert paths.config_file.exists()
    assert paths.env_file.exists()

    cfg_text = paths.config_file.read_text(encoding="utf-8")
    env_text = paths.env_file.read_text(encoding="utf-8")

    # Template markers
    assert "# hlpr configuration file" in cfg_text
    assert "OPENAI_API_KEY" in env_text
