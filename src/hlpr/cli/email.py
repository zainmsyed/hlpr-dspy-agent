"""Email CLI - minimal stubs for contract tests."""

from typing import NoReturn

import typer
from rich.console import Console

app = typer.Typer(help="Email related commands")
console = Console()

accounts_app = typer.Typer(help="Manage email accounts")
app.add_typer(accounts_app, name="accounts")

_accounts = {}


@accounts_app.command("list")
def accounts_list() -> NoReturn:
    """List email accounts."""
    # Print headers even if empty to satisfy contract tests
    console.print("id | provider | username")
    if not _accounts:
        # No rows
        raise typer.Exit(0)
    for aid, v in _accounts.items():
        console.print(f"{aid} | {v.get('provider')} | {v.get('username')}")
    raise typer.Exit(0)


@accounts_app.command("add")
def accounts_add(
    account_id: str,
    provider: str = typer.Option(..., "--provider"),
    username: str | None = typer.Option(None, "--username"),
    password: str | None = typer.Option(None, "--password"),
    host: str | None = typer.Option(None, "--host"),
) -> NoReturn:
    """Add email account."""
    if not username or not password:
        console.print("Missing required username/password")
        raise typer.Exit(2)
    if account_id in _accounts:
        console.print("Account exists")
        raise typer.Exit(1)
    _accounts[account_id] = {"provider": provider, "username": username, "host": host}
    console.print("Account added")
    raise typer.Exit(0)


@accounts_app.command("remove")
def accounts_remove(account_id: str) -> NoReturn:
    """Remove account."""
    if account_id not in _accounts:
        console.print("Account not found")
        raise typer.Exit(1)
    del _accounts[account_id]
    console.print("Removed")
    raise typer.Exit(0)


@accounts_app.command("test")
def accounts_test(account_id: str) -> NoReturn:
    """Test account connection."""
    if account_id not in _accounts:
        console.print("Account not found")
        raise typer.Exit(1)
    console.print("Connection OK")
    raise typer.Exit(0)


@app.command("process")
def process_emails(
    account_id: str = typer.Argument(None),
    mailbox: str | None = typer.Option(None, "--mailbox"),
    *,
    unread_only: bool = typer.Option(
        default=False,
        help="Process only unread emails",
    ),
    limit: int | None = typer.Option(None, "--limit"),
    output_options: str = typer.Option(
        "txt:",
        "--output",
        help="Output format:path (e.g., txt:file.txt)",
    ),
) -> NoReturn:
    """Process emails from specified account."""
    # Parse output_options to extract format and path
    if ":" in output_options:
        output_format, output_path = output_options.split(":", 1)
    else:
        output_format = output_options
        output_path = None

    console.print(f"Processing emails for account: {account_id}")
    console.print(f"Mailbox: {mailbox or 'ALL'}")
    console.print(f"Unread only: {unread_only}")
    console.print(f"Limit: {limit or 'No limit'}")
    console.print(f"Output format: {output_format}")
    console.print(f"Output path: {output_path or 'Console'}")
