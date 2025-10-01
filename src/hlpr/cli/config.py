"""Config CLI - setup and management commands."""

import os
from typing import NoReturn

import typer
from rich.console import Console

from hlpr.config.manager import ConfigurationManager
from hlpr.config.models import (
    APICredentials,
    ConfigurationPaths,
    ConfigurationState,
    OutputFormat,
    ProviderType,
    UserConfiguration,
)
from hlpr.models.user_preferences import PreferencesStore, UserPreferences

app = typer.Typer(help="Configuration commands")
console = Console()


def _simulated_prompts() -> list[str]:
    """Return a list of simulated prompt responses from env var HLPR_SIMULATED_PROMPTS.

    The env var should be newline-separated responses. This is intended for tests
    to avoid dealing with interactive tty prompts.
    """
    raw = os.environ.get("HLPR_SIMULATED_PROMPTS")
    if not raw:
        return []
    return [line.rstrip("\r") for line in raw.split("\n")]


_SIM_PROMPTS = None


def _next_simulated_response() -> str | None:
    global _SIM_PROMPTS
    if _SIM_PROMPTS is None:
        _SIM_PROMPTS = _simulated_prompts()
    if not _SIM_PROMPTS:
        return None
    return _SIM_PROMPTS.pop(0)


# Preferences sub-app
preferences_app = typer.Typer(name="preferences", help="Manage user preferences")


@preferences_app.command("show")
def show_preferences() -> None:
    """Show stored user preferences."""
    store = PreferencesStore()
    prefs = store.load()
    console.print_json(
        data={
            "theme": prefs.theme,
            "last_provider": prefs.last_provider,
            "last_format": prefs.last_format,
        }
    )
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


def _prompt_choice(prompt: str, choices: list[str], default: str) -> str:
    console.print(f"Available: {', '.join(choices)}")
    # Allow tests to inject simulated responses via HLPR_SIMULATED_PROMPTS
    sim = _next_simulated_response()
    if sim is not None:
        val = sim or default
    else:
        val = typer.prompt(f"{prompt} [{default}]") or default
    while val not in choices:
        console.print(f"Invalid choice: {val}")
        sim = _next_simulated_response()
        if sim is not None:
            val = sim or default
        else:
            val = typer.prompt(f"{prompt} [{default}]") or default
    return val


@app.command("setup")
def setup_config(
    non_interactive: bool = typer.Option(
        False, "--non-interactive", help="Run setup without interactive prompts"
    ),
) -> None:
    """Run guided setup for configuration.

    Interactive mode will prompt for provider, output format, temperature, max tokens and optional API key.
    Pass --non-interactive to initialize with defaults (useful in scripts/tests).
    """
    paths = ConfigurationPaths.default()
    mgr = ConfigurationManager(paths=paths)

    if mgr.is_first_run():
        if non_interactive:
            state = mgr.load_configuration()
            mgr.save_configuration(state)
            console.print(f"Configuration initialized at {paths.config_dir}")
            raise typer.Exit(0)

        # Interactive flow
        console.print("Welcome to hlpr guided setup")

        # Provider
        default_provider = ProviderType.LOCAL.value
        provider_choice = _prompt_choice(
            "Choose default provider", [p.value for p in ProviderType], default_provider
        )
        provider = ProviderType(provider_choice)

        # Output format
        default_format = OutputFormat.RICH.value
        fmt_choice = _prompt_choice(
            "Default output format", [f.value for f in OutputFormat], default_format
        )
        out_format = OutputFormat(fmt_choice)

        # Temperature
        temp_default = 0.3
        sim = _next_simulated_response()
        if sim is not None:
            temp_raw = sim or str(temp_default)
        else:
            temp_raw = typer.prompt(f"Default temperature [{temp_default}]") or str(
                temp_default
            )
        try:
            temperature = float(temp_raw)
        except Exception:
            console.print("Invalid temperature; using default 0.3")
            temperature = temp_default

        # Max tokens
        max_default = 8192
        sim = _next_simulated_response()
        if sim is not None:
            max_raw = sim or str(max_default)
        else:
            max_raw = typer.prompt(f"Default max tokens [{max_default}]") or str(
                max_default
            )
        try:
            max_tokens = int(max_raw)
        except Exception:
            console.print(f"Invalid max tokens; using default {max_default}")
            max_tokens = max_default

        creds = APICredentials()
        # Prompt for API key when provider is not local
        if provider != ProviderType.LOCAL:
            key_prompt = f"Enter API key for {provider.value} (leave blank to skip)"
            # Check for simulated value first
            sim = _next_simulated_response()
            if sim is not None:
                api_key = sim
            else:
                # hide input when available
                api_key = typer.prompt(key_prompt, hide_input=True)
            if api_key:
                # Set the appropriate field on APICredentials
                if provider == ProviderType.OPENAI:
                    creds.openai_api_key = api_key
                elif provider == ProviderType.GOOGLE:
                    creds.google_api_key = api_key
                elif provider == ProviderType.ANTHROPIC:
                    creds.anthropic_api_key = api_key
                elif provider == ProviderType.OPENROUTER:
                    creds.openrouter_api_key = api_key
                elif provider == ProviderType.GROQ:
                    creds.groq_api_key = api_key
                elif provider == ProviderType.DEEPSEEK:
                    creds.deepseek_api_key = api_key
                elif provider == ProviderType.GLM:
                    creds.glm_api_key = api_key
                elif provider == ProviderType.COHERE:
                    creds.cohere_api_key = api_key
                elif provider == ProviderType.MISTRAL:
                    creds.mistral_api_key = api_key

        config = UserConfiguration(
            default_provider=provider,
            default_format=out_format,
            default_temperature=temperature,
            default_max_tokens=max_tokens,
        )

        state = ConfigurationState(config=config, credentials=creds)
        mgr.save_configuration(state)
        console.print(f"Configuration initialized and saved to {paths.config_file}")
        raise typer.Exit(0)

    # Not first run
    console.print(
        "Configuration already exists. Use 'hlpr config reset' to reset or 'hlpr config show' to view."
    )
    raise typer.Exit(0)


@app.command("validate")
def validate_config() -> None:
    """Validate current configuration files."""
    paths = ConfigurationPaths.default()
    mgr = ConfigurationManager(paths=paths)
    result = mgr.validate_configuration()
    if result.is_valid:
        console.print("Configuration is valid")
        raise typer.Exit(0)
    console.print_json(data={"errors": result.errors, "warnings": result.warnings})
    raise typer.Exit(1)


@app.command("reset")
def reset_config(backup: bool = typer.Option(True, "--backup/--no-backup")) -> None:
    paths = ConfigurationPaths.default()
    mgr = ConfigurationManager(paths=paths)
    if backup:
        b = mgr.backup_config()
        if b:
            console.print(f"Backed up configuration to: {b}")
    # Remove files
    try:
        if paths.config_file.exists():
            paths.config_file.unlink()
        if paths.env_file.exists():
            paths.env_file.unlink()
        console.print("Configuration reset to defaults")
        raise typer.Exit(0)
    except Exception as exc:
        console.print(f"Failed to reset configuration: {exc}")
        raise typer.Exit(1) from exc


@app.command("show")
def show_config(
    output_format: str = typer.Option("text", "--format"),
    hide_sensitive: bool = typer.Option(False),
) -> None:
    """Show configuration."""
    paths = ConfigurationPaths.default()
    mgr = ConfigurationManager(paths=paths)
    state = mgr.load_configuration()
    cfg = state.config
    creds = state.credentials
    if output_format == "json":
        out = {
            "config": cfg.model_dump() if hasattr(cfg, "model_dump") else cfg.dict(),
            "credentials": {
                k: ("***" if hide_sensitive and v else (v or ""))
                for k, v in (
                    creds.model_dump().items()
                    if hasattr(creds, "model_dump")
                    else creds.dict().items()
                )
            },
        }
        console.print_json(data=out)
        raise typer.Exit(0)
    # text format
    for k, v in (
        cfg.model_dump().items() if hasattr(cfg, "model_dump") else cfg.dict().items()
    ):
        console.print(f"{k}: {v}")
    if hide_sensitive:
        console.print("credentials: ****")
    else:
        console.print("credentials: present")
    raise typer.Exit(0)


# Mount guided-mode config commands (lazy import to avoid heavy imports at module load)
try:
    from hlpr.cli import config_commands as _config_commands_module

    app.add_typer(_config_commands_module.app, name="guided")
except Exception:
    # If import fails (e.g., in some tests or trimmed environments), skip wiring.
    pass


@app.command("set")
def set_config(key: str, value: str) -> NoReturn:
    """Set configuration value (in-memory stub)."""
    # Persist simple key/value pairs in a kv.json inside the config dir
    paths = ConfigurationPaths.default()
    mgr = ConfigurationManager(paths=paths)
    kv_path = paths.config_dir / "kv.json"

    # Load existing kv store
    store: dict = {}
    if kv_path.exists():
        try:
            import json

            with open(kv_path, encoding="utf-8") as f:
                store = json.load(f) or {}
        except Exception:
            store = {}

    store[key] = value

    # Write atomically (isolate write errors so we don't catch the intended Exit)
    import json

    text = json.dumps(store, indent=2)
    try:
        mgr._atomic_write(kv_path, text)
    except Exception as exc:
        console.print(f"Failed to set key: {exc}")
        raise typer.Exit(1) from exc

    console.print(f"Set {key}")
    raise typer.Exit(0)


@app.command("get")
def get_config(key: str = typer.Argument(None)) -> NoReturn:
    """Get configuration value (in-memory stub)."""
    if key is None:
        console.print("Missing key")
        raise typer.Exit(2)
    paths = ConfigurationPaths.default()
    kv_path = paths.config_dir / "kv.json"
    if not kv_path.exists():
        console.print("Not found")
        raise typer.Exit(1)

    import json

    try:
        with open(kv_path, encoding="utf-8") as f:
            store = json.load(f) or {}
    except (OSError, json.JSONDecodeError) as exc:
        console.print("Not found")
        raise typer.Exit(1) from exc

    if key not in store:
        console.print("Not found")
        raise typer.Exit(1)

    console.print(store[key])
    raise typer.Exit(0)


@app.command("edit")
def edit_config(
    editor: str = typer.Option(
        "", "--editor", help="Editor command to use (overrides $EDITOR)"
    ),
) -> NoReturn:
    """Open the configuration file in the user's editor.

    If no editor is available, return exit code 2 to indicate no-op in tests.
    """
    paths = ConfigurationPaths.default()
    cfg = paths.config_file
    # Ensure config exists
    if not cfg.exists():
        # Create default config first
        mgr = ConfigurationManager(paths=paths)
        mgr.save_configuration(mgr.load_configuration())

    cmd = editor or os.environ.get("EDITOR")
    if not cmd:
        console.print("No editor configured ($EDITOR or --editor)")
        raise typer.Exit(2)

    # Attempt to launch editor (blocking). For tests, callers can pass --editor "true" or similar.
    try:
        import shlex
        import subprocess

        parts = [*shlex.split(cmd), str(cfg)]
        subprocess.check_call(parts)
        raise typer.Exit(0)
    except subprocess.CalledProcessError as exc:
        console.print("Editor returned non-zero exit")
        raise typer.Exit(1) from exc
    except Exception as exc:
        console.print(f"Failed to open editor: {exc}")
        raise typer.Exit(1) from exc
