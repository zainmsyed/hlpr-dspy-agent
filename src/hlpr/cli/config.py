"""Config CLI - setup and management commands."""

import os
from typing import NoReturn

import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm

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


def _warn_if_backup(mgr: ConfigurationManager) -> None:
    """Print a concise warning if the manager recorded a backup during load.

    This is a small UX improvement so users notice when their config was
    preserved and defaults are in use.
    """
    try:
        if getattr(mgr, "last_backup_path", None):
            # Use stderr so we don't pollute stdout (important when callers
            # expect machine-readable output, e.g., JSON).
            from rich.console import Console as _Console

            _err_console = _Console(stderr=True)
            _err_console.print(
                f"[yellow]Warning:[/yellow] configuration was backed up to {mgr.last_backup_path} ({mgr.last_backup_reason or 'corrupt'}) and defaults are in use."
            )
    except Exception:
        # best-effort, don't raise in CLI
        pass


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
        val = Prompt.ask(prompt, choices=choices, default=default)
    while val not in choices:
        console.print(f"Invalid choice: {val}")
        sim = _next_simulated_response()
        if sim is not None:
            val = sim or default
        else:
            val = Prompt.ask(prompt, choices=choices, default=default)
    return val


@app.command("setup")
def setup_config(
    non_interactive: bool = typer.Option(
        False, "--non-interactive", help="Run setup without interactive prompts"
    ),
    force: bool = typer.Option(
        False, "--force", help="Run setup even if configuration already exists"
    ),
) -> None:
    """Run guided setup for configuration.

    Interactive mode will prompt for provider, output format, temperature, max tokens and optional API key.
    Pass --non-interactive to initialize with defaults (useful in scripts/tests).
    """
    paths = ConfigurationPaths.default()
    mgr = ConfigurationManager(paths=paths)

    is_first = mgr.is_first_run()

    # Decide whether to run setup: if first-run or --force or non_interactive we
    # run automatically; otherwise prompt the user.
    should_run = False
    if is_first or force or non_interactive:
        should_run = True
    else:
        # Support simulated responses for tests via HLPR_SIMULATED_PROMPTS
        sim = _next_simulated_response()
        if sim is not None:
            proceed = sim.lower() in ("y", "yes", "true", "1")
        else:
            proceed = Confirm.ask("Configuration already exists. Run guided setup anyway?", default=False)
        if not proceed:
            console.print(
                "Configuration already exists. Use 'hlpr config reset' to reset or 'hlpr config show' to view."
            )
            raise typer.Exit(0)
        should_run = True

    if should_run:
        if non_interactive:
            state = mgr.load_configuration()
            _warn_if_backup(mgr)
            mgr.save_configuration(state)
            # Initialize guided-mode config defaults as well
            try:
                from hlpr.cli import config_commands

                # Use the module-level function to create/reset guided config
                # without creating a backup (non-interactive init)
                config_commands.reset(backup=False)
            except Exception:
                # best-effort: guided config initialization should not fail setup
                pass
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
        # Temperature: validate numeric input and enforce range [0.0, 1.0]
        temperature = temp_default
        while True:
            sim = _next_simulated_response()
            if sim is not None:
                temp_raw = sim or str(temp_default)
            else:
                temp_raw = Prompt.ask(
                    "Default temperature (0.0 - 1.0)", default=str(temp_default)
                )
            try:
                val = float(temp_raw)
            except Exception:
                console.print(
                    f"Invalid temperature '{temp_raw}'; enter a number between 0.0 and 1.0"
                )
                # reprompt
                continue
            if not (0.0 <= val <= 1.0):
                console.print(
                    f"Temperature {val} out of range; please enter a value between 0.0 and 1.0"
                )
                continue
            temperature = val
            break

        # Max tokens
        max_default = 8192
        sim = _next_simulated_response()
        if sim is not None:
            max_raw = sim or str(max_default)
        else:
            max_raw = Prompt.ask("Default max tokens", default=str(max_default))
        try:
            max_tokens = int(max_raw)
        except Exception:
            console.print(f"Invalid max tokens; using default {max_default}")
            max_tokens = max_default

        creds = APICredentials()
        # Prompt for API key when provider is not local
        if provider != ProviderType.LOCAL:
            key_prompt = f"Enter API key for {provider.value} (leave blank to skip)"
            # Check for simulated value first (tests)
            sim = _next_simulated_response()
            if sim is not None:
                api_key = sim
            else:
                # hide input when available
                api_key = Prompt.ask(key_prompt, password=True)
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
        # Also initialize guided-mode configuration with defaults and create a
        # backup of any existing guided config so users have a sane guided
        # workflow out of the box.
        try:
            from hlpr.cli import config_commands

            config_commands.reset(backup=True)
        except Exception:
            # best-effort
            pass
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
    # validate_configuration will call load_configuration internally when
    # no state is provided; warn if load resulted in a backup.
    result = mgr.validate_configuration()
    _warn_if_backup(mgr)
    if result.is_valid:
        console.print("Configuration is valid")
        raise typer.Exit(0)
    console.print_json(data={"errors": result.errors, "warnings": result.warnings})
    raise typer.Exit(1)


@app.command("reset")
def reset_config(
    backup: bool = typer.Option(True, "--backup/--no-backup"),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation"),
) -> None:
    """Reset configuration to defaults.

    By default this prompts for confirmation and creates a manual backup. Use
    `--no-backup` to skip creating a backup, or `--yes` to skip confirmation.
    """
    paths = ConfigurationPaths.default()
    mgr = ConfigurationManager(paths=paths)

    if not yes:
        sim = _next_simulated_response()
        if sim is not None:
            confirm = sim.lower() in ("y", "yes", "true", "1")
        else:
            confirm = Confirm.ask(
                "This will back up your current configuration and reset to defaults. Continue?",
                default=False,
            )
        if not confirm:
            console.print("Aborted")
            raise typer.Exit(0)

    if backup:
        b = mgr.backup_config()
        if b:
            console.print(f"Backed up configuration to: {b}")

    # Write default configuration (safer: keep a known-good state)
    from hlpr.config.models import ConfigurationState

    try:
        default_state = ConfigurationState()
        mgr.save_configuration(default_state)
        console.print("Configuration reset to defaults")
        raise typer.Exit(0)
    except typer.Exit:
        # Propagate Typer/CLI exit requests unchanged
        raise
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
    # Avoid printing warnings to stdout when caller requested JSON output.
    if output_format != "json":
        _warn_if_backup(mgr)
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
# Guided-mode commands are initialized as part of `config setup` so we do not
# mount a separate `config guided` subcommand here. See `src/hlpr/cli/config_commands.py`.


# Backups sub-app
backups_app = typer.Typer(name="backups", help="Manage configuration backups")


@backups_app.command("list")
def list_backups() -> None:
    """List available backups (corrupted flat backups and manual timestamped backups)."""
    paths = ConfigurationPaths.default()
    bdir = paths.backup_dir
    if not bdir.exists():
        console.print("No backups found")
        raise typer.Exit(0)

    # List flat corrupted backups first
    corrupted = sorted(
        [p for p in bdir.iterdir() if p.is_file() and p.name.startswith("config.yaml.corrupted")],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if corrupted:
        console.print("Corrupted backups:")
        for p in corrupted:
            console.print(f"- {p.name} ({p.stat().st_mtime})")

    # Then list manual timestamped backup subdirs
    subdirs = sorted(
        [p for p in bdir.iterdir() if p.is_dir()],
        key=lambda p: p.name,
        reverse=True,
    )
    if subdirs:
        console.print("Manual backups:")
        for d in subdirs:
            console.print(f"- {d.name}")

    raise typer.Exit(0)


@backups_app.command("restore")
def restore_backup(name: str) -> None:
    """Restore a named backup. For corrupted flat backups pass the filename, for manual backups pass the subdir name."""
    paths = ConfigurationPaths.default()
    mgr = ConfigurationManager(paths=paths)
    bdir = paths.backup_dir
    target = bdir / name
    # If name corresponds to a flat file, attempt to restore
    if target.is_file():
        # Move backed up file into place
        try:
            mgr.paths.config_dir.mkdir(parents=True, exist_ok=True)
            target_path = mgr.paths.config_file
            # copy the file from backup to config path
            import shutil

            shutil.copy2(target, target_path)
            console.print(f"Restored {name} to {target_path}")
            raise typer.Exit(0)
        except Exception as exc:
            console.print(f"Failed to restore backup: {exc}")
            raise typer.Exit(1) from exc

    # If it's a subdir
    sub = bdir / name
    if sub.is_dir():
        ok = mgr.restore_backup(sub)
        if ok:
            console.print(f"Restored backup from {sub}")
            raise typer.Exit(0)
        console.print(f"Failed to restore from {sub}")
        raise typer.Exit(1)

    console.print("Backup not found")
    raise typer.Exit(2)


@backups_app.command("delete")
def delete_backup(name: str) -> None:
    """Delete a named backup (file or subdir)."""
    paths = ConfigurationPaths.default()
    bdir = paths.backup_dir
    target = bdir / name
    try:
        if target.is_file():
            target.unlink()
            console.print(f"Deleted {name}")
            raise typer.Exit(0)
        if target.is_dir():
            import shutil

            shutil.rmtree(target)
            console.print(f"Deleted {name}")
            raise typer.Exit(0)
    except Exception as exc:
        console.print(f"Failed to delete backup: {exc}")
        raise typer.Exit(1) from exc

    console.print("Backup not found")
    raise typer.Exit(2)


app.add_typer(backups_app, name="backups")


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
        _warn_if_backup(mgr)

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
