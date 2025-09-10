"""Main CLI application for hlpr."""

import typer
from rich.console import Console

from hlpr.cli.summarize import app as summarize_app

# Create main app
app = typer.Typer(
    name="hlpr",
    help="Personal AI Assistant",
    add_completion=False,
)

# Add subcommands
app.add_typer(summarize_app, name="summarize")

# Global console for rich output
console = Console()


@app.callback()
def main_callback(
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose output"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress non-essential output"),
    config: str = typer.Option(None, "--config", help="Custom configuration file path"),
):
    """Personal AI Assistant CLI."""
    # Store global options for use in subcommands
    app.verbose = verbose
    app.quiet = quiet
    app.config = config


@app.command()
def version():
    """Show version information."""
    console.print("hlpr v0.1.0")
    console.print("Personal AI Assistant")


if __name__ == "__main__":
    app()