"""Help display utilities for the guided interactive workflow.

Provides a small, test-friendly API to show provider/format help and
general quick-help panels. Designed to be injectable into InteractiveSession
so UI implementations can render consistent help content.
"""
from __future__ import annotations

from rich.console import Console
from rich.panel import Panel

from hlpr.config.ui_strings import (
    FORMAT_HELP,
    NO_HELP_AVAILABLE,
    PANEL_FORMAT_HELP,
    PANEL_PROVIDER_HELP,
    PROVIDER_HELP,
    QUICK_HELP,
)

__all__ = ["HelpDisplay"]


class HelpDisplay:
    """Render small help panels for interactive prompts.

    The class is intentionally minimal so it can be used in unit tests by
    passing a `Console(record=True)` instance.
    """

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def show_provider_help(self, provider: str | None = None) -> None:
        """Show help for a specific provider or a summary for all providers."""
        if provider:
            text = PROVIDER_HELP.get(provider, NO_HELP_AVAILABLE.format(name=provider))
            panel = Panel(text, title=f"Provider: {provider}")
        else:
            body = "\n".join(f"[bold]{k}[/bold]: {v}" for k, v in PROVIDER_HELP.items())
            panel = Panel(body, title=PANEL_PROVIDER_HELP)
        self.console.print(panel)

    def show_format_help(self, fmt: str | None = None) -> None:
        """Show help for a specific output format or all formats."""
        if fmt:
            text = FORMAT_HELP.get(fmt, NO_HELP_AVAILABLE.format(name=fmt))
            panel = Panel(text, title=f"Format: {fmt}")
        else:
            body = "\n".join(f"[bold]{k}[/bold]: {v}" for k, v in FORMAT_HELP.items())
            panel = Panel(body, title=PANEL_FORMAT_HELP)
        self.console.print(panel)

    def show_quick_help(self) -> None:
        """Show a compact quick help panel for guided mode usage."""
        panel = Panel(QUICK_HELP, title=PANEL_PROVIDER_HELP + " Quick Help")
        self.console.print(panel)
