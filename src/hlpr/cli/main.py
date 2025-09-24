"""Main CLI application for hlpr."""

import typer
from rich.console import Console

from hlpr.cli import config as config_module
from hlpr.cli import email as email_module
from hlpr.cli import providers as providers_module
from hlpr.cli.summarize import app as summarize_app
from hlpr.cli import template_commands as template_commands_module

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


@app.command()
def version() -> None:
    """Show version information."""
    console.print("hlpr v0.1.0")
    console.print("Personal AI Assistant")


if __name__ == "__main__":
    app()


def main() -> None:
    """Entry point for console scripts: run the Typer app."""
    app()
