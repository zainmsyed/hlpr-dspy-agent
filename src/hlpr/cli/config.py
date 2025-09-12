"""Config CLI - minimal stubs for contract tests."""

from typing import NoReturn

import typer
from rich.console import Console

app = typer.Typer(help="Configuration commands")
console = Console()

_config = {
    "default_llm": "local",
    "providers": {},
}


@app.command("show")
def show_config(
    output_format: str = typer.Option("text", "--format"),
    *,
    hide_sensitive: bool = typer.Option(
        default=False,
        help="Hide sensitive configuration values",
    ),
) -> NoReturn:
    """Show configuration."""
    if output_format == "json":
        console.print_json(data=_config)
    else:
        # Print YAML-like output for readability and tests
        for k, v in _config.items():
            if hide_sensitive and "key" in k.lower():
                console.print(f"{k}: ****")
            else:
                console.print(f"{k}: {v}")
        # Also print known top-level keys on separate lines
        if "default_llm" in _config:
            console.print(f"default_llm: {_config['default_llm']}")
        if "providers" in _config:
            console.print(f"providers: {_config['providers']}")
    raise typer.Exit(0)


@app.command("set")
def set_config(key: str, value: str) -> NoReturn:
    """Set configuration value."""
    if "." in key:
        console.print("Invalid key")
        raise typer.Exit(1)
    _config[key] = value
    console.print(f"Set {key}")
    raise typer.Exit(0)


@app.command("get")
def get_config(key: str = typer.Argument(None)) -> NoReturn:
    """Get configuration value."""
    if key is None:
        console.print("Missing key")
        raise typer.Exit(2)
    if key not in _config:
        console.print("Not found")
        raise typer.Exit(1)
    console.print(_config[key])
    raise typer.Exit(0)
