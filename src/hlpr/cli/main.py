"""Main CLI application for hlpr."""

import typer
from rich.console import Console

from hlpr.cli import config as config_module
from hlpr.cli import email as email_module
from hlpr.cli import providers as providers_module
from hlpr.cli import template_commands as template_commands_module
from hlpr.cli.summarize import app as summarize_app

# Create main app
app = typer.Typer(
    name="hlpr",
    help="Personal AI Assistant",
    add_completion=False,
)

# Add subcommands
app.add_typer(summarize_app, name="summarize")
app.add_typer(providers_module.app, name="providers")
app.add_typer(config_module.app, name="config")
app.add_typer(email_module.app, name="email")
app.add_typer(template_commands_module.app, name="template")

# Global console for rich output
console = Console()


@app.callback()
def main_callback(
    config: str = typer.Option(
        None,
        "--config",
        help="Custom configuration file path",
    ),
    *,
    verbose: bool = typer.Option(
        default=False,
        help="Enable verbose output",
    ),
    quiet: bool = typer.Option(
        default=False,
        help="Suppress non-essential output",
    ),
) -> None:
    """Personal AI Assistant CLI."""
    # Store global options for use in subcommands
    app.verbose = verbose
    app.quiet = quiet
    app.config = config

    # Load persisted user configuration early so subcommands can access it.
    # We use a ConfigurationManager to load the YAML + .env state and attach
    # it to the Typer app object for convenient access during command runtime.
    try:
        from hlpr.config.manager import ConfigurationManager
        from hlpr.config.models import ConfigurationPaths

        cfg_paths = ConfigurationPaths.default()
        mgr = ConfigurationManager(paths=cfg_paths)
        try:
            state = mgr.load_configuration()
        except Exception:
            # If loading fails, surface a warning but keep running with defaults
            state = None

        # Attach to app for subcommands to read; avoid overwriting if already set
        app.config_manager = mgr
        app.configuration_state = state
    except Exception:
        # Best-effort: do not break CLI startup if config subsystem is missing
        app.config_manager = None
        app.configuration_state = None


@app.command()
def version() -> None:
    """Show version information."""
    console.print("hlpr v0.1.0")
    console.print("Personal AI Assistant")


@app.command(name="file-picker")
def file_picker_command() -> None:
    """Placeholder for the file-picker command.

    The interactive file picker has been removed for now. Calling this
    command will show a short message rather than attempting to import
    missing module `hlpr.cli.file_picker`.
    """
    from rich.console import Console

    console = Console()
    console.print("The interactive file picker has been removed from this build.")
    # Previously: from hlpr.cli.file_picker import main as fp_main
    # fp_main(root, depth)


if __name__ == "__main__":
    app()


def main() -> None:
    """Entry point for console scripts: run the Typer app."""
    app()
