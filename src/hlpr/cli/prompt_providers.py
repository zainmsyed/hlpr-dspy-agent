"""Pluggable prompt providers for guided workflow.

Defines a PromptProvider protocol and two implementations:
- DefaultPromptProvider: wraps the test-friendly OptionPrompts
- InteractivePromptProvider: uses simple input() prompts (safe fallback)

Notes:
- When the CLI saves summaries (via `--save`), it will by default write
    files into an organized folder at `summaries/documents/` relative
    to the current working directory unless an explicit `--output` path is
    provided.
- When saving and no explicit `--format` is provided, the CLI uses
    Markdown (`.md`) as the default saved format.

InteractiveSession will accept a PromptProvider via DI so the UI can be
swapped for tests or an interactive runtime implementation that uses
Rich/Typer later.
"""

from __future__ import annotations

from typing import Any, Protocol

import typer
from rich.console import Console

from hlpr.cli.help_display import HelpDisplay
from hlpr.cli.prompts import OptionPrompts


class PromptProvider(Protocol):
    def provider_prompt(self) -> str: ...

    def format_prompt(self) -> str: ...

    def save_file_prompt(self) -> tuple[bool, str | None]: ...

    def temperature_prompt(self) -> float: ...

    def advanced_options_prompt(self) -> dict[str, Any]: ...


class DefaultPromptProvider:
    """Default provider that delegates to OptionPrompts (test-friendly)."""

    def __init__(self, defaults: dict[str, Any] | None = None) -> None:
        self.prompts = OptionPrompts(defaults)

    def provider_prompt(self) -> str:
        return self.prompts.provider_prompt()

    def format_prompt(self) -> str:
        return self.prompts.format_prompt()

    def save_file_prompt(self) -> tuple[bool, str | None]:
        return self.prompts.save_file_prompt()

    def temperature_prompt(self) -> float:
        return self.prompts.temperature_prompt()

    def advanced_options_prompt(self) -> dict[str, Any]:
        return self.prompts.advanced_options_prompt()


class InteractivePromptProvider:
    """A minimal interactive provider using input(); meant for simple CLI runs.

    This is intentionally lightweight: future versions can implement a
    Rich/Typer-based provider and still comply with the PromptProvider
    protocol.
    """

    def __init__(self, defaults: dict[str, Any] | None = None) -> None:
        self.defaults = defaults or {}
        # Use OptionPrompts for validation helpers and to obtain max attempts
        self._prompts = OptionPrompts(self.defaults)
        # HelpDisplay used to show contextual help when validation fails
        self._help = self.defaults.get("help_display") or HelpDisplay()

    def _input_with_default(self, prompt: str, default: str) -> str:
        try:
            res = input(f"{prompt} [{default}]: ")
        except EOFError:
            return default
        return res.strip() or default

    def provider_prompt(self) -> str:
        default = str(self.defaults.get("provider", "local"))
        max_attempts = int(
            self.defaults.get("max_attempts", self._prompts.max_attempts)
        )
        for _ in range(max_attempts):
            candidate = self._input_with_default("Provider", default)
            valid, msg = self._prompts.validate_provider(candidate)
            if valid:
                return candidate
            # validation failed: show message and contextual help
            typer.echo(f"Invalid provider: {msg}")
            self._help.show_provider_help()
        # fallback to default after attempts exhausted
        typer.echo(f"Max attempts exceeded, using default provider: {default}")
        return default

    def format_prompt(self) -> str:
        default = str(self.defaults.get("format", "rich"))
        max_attempts = int(
            self.defaults.get("max_attempts", self._prompts.max_attempts)
        )
        for _ in range(max_attempts):
            candidate = self._input_with_default("Format", default)
            valid, msg = self._prompts.validate_format(candidate)
            if valid:
                return candidate
            typer.echo(f"Invalid format: {msg}")
            self._help.show_format_help()
        # fallback after attempts exhausted
        typer.echo(f"Max attempts exceeded, using default format: {default} (when saving defaults to md)")
        return default

    def save_file_prompt(self) -> tuple[bool, str | None]:
        save_raw = self._input_with_default("Save output? (y/n)", "n")
        save = save_raw.lower() in ("y", "yes")
        path = None
        if save:
            path = self._input_with_default(
                "Output path", str(self.defaults.get("output_path", "output.txt"))
            )
        return save, path

    def temperature_prompt(self) -> float:
        default = float(self.defaults.get("temperature", 0.3))
        max_attempts = int(
            self.defaults.get("max_attempts", self._prompts.max_attempts)
        )
        for _ in range(max_attempts):
            raw = self._input_with_default("Temperature", str(default))
            valid, msg = self._prompts.validate_temperature(raw)
            if valid:
                try:
                    return float(raw)
                except Exception:
                    return default
            typer.echo(f"Invalid temperature: {msg}")
        typer.echo(f"Max attempts exceeded, using default temperature: {default}")
        return default

    def advanced_options_prompt(self) -> dict[str, Any]:
        default = int(self.defaults.get("chunk_size", 8192))
        max_attempts = int(
            self.defaults.get("max_attempts", self._prompts.max_attempts)
        )
        for _ in range(max_attempts):
            chunk = self._input_with_default("Chunk size", str(default))
            try:
                val = int(chunk)
                if val <= 0:
                    raise ValueError("must be > 0")
                return {"chunk_size": val}
            except Exception:
                typer.echo("Chunk size must be a positive integer")
        typer.echo(f"Max attempts exceeded, using default chunk size: {default}")
        return {"chunk_size": default}


class RichTyperPromptProvider:
    """Interactive provider that uses Typer/Rich prompts for a better UX.

    This provider is intended for use when the CLI is attached to a TTY.
    """

    def __init__(self, defaults: dict[str, Any] | None = None) -> None:
        self.defaults = defaults or {}
        self.console = Console()
        self._prompts = OptionPrompts(self.defaults)
        self._help = self.defaults.get("help_display") or HelpDisplay(self.console)

    def provider_prompt(self) -> str:
        default = str(self.defaults.get("provider", "local"))
        max_attempts = int(
            self.defaults.get("max_attempts", self._prompts.max_attempts)
        )
        for _ in range(max_attempts):
            candidate = typer.prompt("Provider", default=default)
            valid, msg = self._prompts.validate_provider(candidate)
            if valid:
                return candidate
            self.console.print(f"[red]Invalid provider:[/red] {msg}")
            self._help.show_provider_help()
        self.console.print(
            f"[yellow]Max attempts exceeded, using default provider:[/yellow] {default}"
        )
        return default

    def format_prompt(self) -> str:
        default = str(self.defaults.get("format", "rich"))
        max_attempts = int(
            self.defaults.get("max_attempts", self._prompts.max_attempts)
        )
        for _ in range(max_attempts):
            candidate = typer.prompt("Output format", default=default)
            valid, msg = self._prompts.validate_format(candidate)
            if valid:
                return candidate
            self.console.print(f"[red]Invalid format:[/red] {msg}")
            self._help.show_format_help()
        self.console.print(
            f"[yellow]Max attempts exceeded, using default format:[/yellow] {default} (when saving defaults to md)"
        )
        return default

    def save_file_prompt(self) -> tuple[bool, str | None]:
        save = typer.confirm(
            "Save output to file?", default=bool(self.defaults.get("save", False))
        )
        path = None
        if save:
            path = typer.prompt(
                "Output path",
                default=str(self.defaults.get("output_path", "output.txt")),
            )
        return save, path

    def temperature_prompt(self) -> float:
        default = float(self.defaults.get("temperature", 0.3))
        max_attempts = int(
            self.defaults.get("max_attempts", self._prompts.max_attempts)
        )
        for _ in range(max_attempts):
            raw = typer.prompt("Temperature", default=str(default))
            valid, msg = self._prompts.validate_temperature(raw)
            if valid:
                try:
                    return float(raw)
                except Exception:
                    return default
            self.console.print(f"[red]Invalid temperature:[/red] {msg}")
        self.console.print(
            f"[yellow]Max attempts exceeded, using default temperature:[/yellow] {default}"
        )
        return default

    def advanced_options_prompt(self) -> dict[str, Any]:
        default = int(self.defaults.get("chunk_size", 8192))
        max_attempts = int(
            self.defaults.get("max_attempts", self._prompts.max_attempts)
        )
        for _ in range(max_attempts):
            chunk = typer.prompt("Chunk size", default=str(default))
            try:
                val = int(chunk)
                if val <= 0:
                    raise ValueError("must be > 0")
                return {"chunk_size": val}
            except Exception:
                self.console.print("[red]Chunk size must be a positive integer[/red]")
        self.console.print(
            f"[yellow]Max attempts exceeded, using default chunk size:[/yellow] {default}"
        )
        return {"chunk_size": default}
