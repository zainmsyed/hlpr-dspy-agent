"""Config CLI - minimal stubs for contract tests."""

from typing import NoReturn

import typer
from rich.console import Console

from hlpr.config import PLATFORM_DEFAULTS
from hlpr.models.user_preferences import PreferencesStore, UserPreferences

app = typer.Typer(help="Configuration commands")
console = Console()

# Preferences sub-app
preferences_app = typer.Typer(name="preferences", help="Manage user preferences")


@preferences_app.command("show")
def show_preferences() -> None:
    """Show stored user preferences."""
    store = PreferencesStore()
    prefs = store.load()
    console.print_json(data={
        "theme": prefs.theme,
        "last_provider": prefs.last_provider,
        "last_format": prefs.last_format,
    })
    raise typer.Exit(0)


@preferences_app.command("set")
def set_preference(key: str, value: str) -> None:
    """Set a preference key to a value. Valid keys: theme, last_provider, last_format"""
    store = PreferencesStore()
    prefs = store.load()
    if not hasattr(prefs, key):
        console.print(f"Invalid preference: {key}")
        raise typer.Exit(2)
    setattr(prefs, key, value)
    store.save(prefs)
    console.print(f"Set preference {key} to {value}")
    raise typer.Exit(0)


@preferences_app.command("reset")
def reset_preferences() -> None:
    """Reset preferences to defaults."""
    store = PreferencesStore()
    prefs = UserPreferences()
    store.save(prefs)
    console.print("Preferences reset to defaults")
    raise typer.Exit(0)


# mount preferences sub-app
app.add_typer(preferences_app, name="preferences")

# Mount guided-mode config commands (lazy import to avoid heavy imports at module load)
try:
    from hlpr.cli import config_commands as _config_commands_module

    app.add_typer(_config_commands_module.app, name="guided")
except Exception:
    # If import fails (e.g., in some tests or trimmed environments), skip wiring.
    pass


_config = {
    "default_llm": PLATFORM_DEFAULTS.default_provider,
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
