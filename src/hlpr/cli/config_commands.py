"""Configuration commands for guided mode.

Provides a small, testable command to reset guided-mode configuration to
project defaults. The implementation intentionally avoids touching global
system state beyond a single config file under the user's home directory
(`~/.hlpr/guided_config.json`) and supports an optional backup.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer
from rich.console import Console

app = typer.Typer(name="guided-config", help="Guided mode configuration commands")
console = Console()


DEFAULTS: dict[str, Any] = {
    "provider": "local",
    "format": "rich",
    "chunk_size": 8192,
    "temperature": 0.3,
}


def config_path() -> Path:
    p = Path.home() / ".hlpr" / "guided_config.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


@app.command("reset")
def reset_config(
    backup: bool = typer.Option(
        True, "--backup/--no-backup", help="Backup existing config before reset"
    ),
) -> None:
    """Reset the guided-mode config file to sane defaults.

    This writes `~/.hlpr/guided_config.json` with DEFAULTS. If a file already
    exists and `--backup` is set, the existing file is copied to the same
    directory with a `.bak` suffix including a timestamp.
    """
    p = config_path()
    if p.exists():
        if backup:
            bak = p.with_suffix(p.suffix + ".bak")
            try:
                bak.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
                console.print(f"Backed up existing config to: {bak}")
            except Exception as exc:
                console.print(f"[red]Failed to backup config:[/] {exc}")
                raise typer.Exit(2) from exc
    try:
        p.write_text(json.dumps(DEFAULTS, indent=2, default=str), encoding="utf-8")
        console.print(f"Reset guided-mode configuration to defaults at {p}")
    except Exception as exc:
        console.print(f"[red]Failed to write config:[/] {exc}")
        raise typer.Exit(1) from exc


@app.command("show")
def show_config() -> None:
    """Show the current guided-mode config (or defaults if missing)."""
    p = config_path()
    if not p.exists():
        console.print_json(data=DEFAULTS)
        raise typer.Exit(0)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        console.print_json(data=data)
    except Exception:
        console.print_json(data=DEFAULTS)
    raise typer.Exit(0)
