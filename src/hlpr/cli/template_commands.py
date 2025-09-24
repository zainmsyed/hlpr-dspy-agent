"""CLI commands to manage saved command templates.

Provides a small Typer sub-app for listing, showing, deleting, and saving
templates. This is intentionally minimal to support integration tests and
future UX enhancements.
"""
from __future__ import annotations

from typing import Optional

import typer

from hlpr.models.saved_commands import SavedCommands
from hlpr.models.templates import CommandTemplate


app = typer.Typer(name="template")


@app.command("list")
def list_templates() -> None:
    """List saved command templates."""
    store = SavedCommands()
    templates = store.load_commands()
    if not templates:
        typer.echo("No saved templates found.")
        raise typer.Exit(0)
    for t in templates:
        typer.echo(f"{t.id}: {t.command_template.splitlines()[0]}...")


@app.command("show")
def show_template(template_id: Optional[str] = typer.Argument(None, help="Template id to show")) -> None:
    """Show a saved template by id.

    If no TEMPLATE_ID is provided, list available templates and prompt the
    user to select one interactively.
    """
    store = SavedCommands()
    templates = store.load_commands()

    if not templates:
        typer.echo("No saved templates found.")
        raise typer.Exit(0)

    # If no id provided, present an interactive numbered list for selection.
    if template_id is None:
        from rich.console import Console
        from rich.prompt import IntPrompt
        from rich.table import Table
        from rich.panel import Panel

        console = Console()

        # Build a table of templates for a pretty panel view
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("#", width=3)
        table.add_column("ID", overflow="fold")
        table.add_column("Preview", overflow="fold")

        for i, t in enumerate(templates, start=1):
            first_line = t.command_template.splitlines()[0]
            preview = first_line if len(first_line) <= 120 else first_line[:117] + "..."
            table.add_row(str(i), t.id, preview)

        console.print(Panel(table, title="Saved Templates", expand=False))

        # Prompt loop using Rich IntPrompt with range validation
        min_choice = 1
        max_choice = len(templates)
        default_choice = 1
        while True:
            try:
                choice = IntPrompt.ask(
                    f"🚀 Select template number (between {min_choice} and {max_choice})",
                    default=default_choice,
                )
                if choice is None:
                    # Accept default
                    idx = default_choice - 1
                    break
                if not (min_choice <= int(choice) <= max_choice):
                    console.print(f"💩 Number must be between {min_choice} and {max_choice}")
                    continue
                idx = int(choice) - 1
                break
            except KeyboardInterrupt:
                raise typer.Exit(1)
            except Exception:
                console.print("💩 Invalid input — please enter a number")
                continue

        selected = templates[idx]
        typer.echo(selected.command_template)
        raise typer.Exit(0)

    # If id provided, show matching template
    for t in templates:
        if t.id == template_id:
            typer.echo(t.command_template)
            raise typer.Exit(0)
    typer.echo(f"Template not found: {template_id}")
    raise typer.Exit(2)


@app.command("delete")
def delete_template(template_id: str) -> None:
    """Delete a saved template by id."""
    store = SavedCommands()
    templates = store.load_commands()
    remaining = [t for t in templates if t.id != template_id]
    if len(remaining) == len(templates):
        typer.echo(f"Template not found: {template_id}")
        raise typer.Exit(2)
    # overwrite storage
    store._atomic_write(remaining)  # reuse internal helper
    typer.echo(f"Deleted template {template_id}")


@app.command("save")
def save_template(command: str, name: Optional[str] = None) -> None:
    """Save a raw command string as a template."""
    store = SavedCommands()
    from datetime import datetime, timezone
    tmpl = CommandTemplate.from_options(
        id=f"cmd_{int(datetime.now(timezone.utc).timestamp())}",
        command_template=command,
        options={},
    )
    try:
        store.save_command(tmpl)
        typer.echo(f"Saved template {tmpl.id}")
    except Exception as exc:
        typer.echo(f"Failed to save template: {exc}")
        raise typer.Exit(1)
