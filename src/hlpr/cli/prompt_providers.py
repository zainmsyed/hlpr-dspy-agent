"""Pluggable prompt providers for guided workflow.

Defines a PromptProvider protocol and two implementations:
- DefaultPromptProvider: wraps the test-friendly OptionPrompts
- InteractivePromptProvider: uses simple input() prompts (safe fallback)

InteractiveSession will accept a PromptProvider via DI so the UI can be
swapped for tests or an interactive runtime implementation that uses
Rich/Typer later.
"""
from __future__ import annotations

from typing import Any, Protocol

import typer
from rich.console import Console

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

    def _input_with_default(self, prompt: str, default: str) -> str:
        try:
            res = input(f"{prompt} [{default}]: ")
        except EOFError:
            return default
        return res.strip() or default

    def provider_prompt(self) -> str:
        return self._input_with_default("Provider", str(self.defaults.get("provider", "local")))

    def format_prompt(self) -> str:
        return self._input_with_default("Format", str(self.defaults.get("format", "rich")))

    def save_file_prompt(self) -> tuple[bool, str | None]:
        save_raw = self._input_with_default("Save output? (y/n)", "n")
        save = save_raw.lower() in ("y", "yes")
        path = None
        if save:
            path = self._input_with_default("Output path", str(self.defaults.get("output_path", "output.txt")))
        return save, path

    def temperature_prompt(self) -> float:
        raw = self._input_with_default("Temperature", str(self.defaults.get("temperature", 0.3)))
        try:
            return float(raw)
        except Exception:
            return float(self.defaults.get("temperature", 0.3))

    def advanced_options_prompt(self) -> dict[str, Any]:
        chunk = self._input_with_default("Chunk size", str(self.defaults.get("chunk_size", 8192)))
        try:
            return {"chunk_size": int(chunk)}
        except Exception:
            return {"chunk_size": int(self.defaults.get("chunk_size", 8192))}


class RichTyperPromptProvider:
    """Interactive provider that uses Typer/Rich prompts for a better UX.

    This provider is intended for use when the CLI is attached to a TTY.
    """

    def __init__(self, defaults: dict[str, Any] | None = None) -> None:
        self.defaults = defaults or {}
        self.console = Console()

    def provider_prompt(self) -> str:
        return typer.prompt("Provider", default=str(self.defaults.get("provider", "local")))

    def format_prompt(self) -> str:
        return typer.prompt("Output format", default=str(self.defaults.get("format", "rich")))

    def save_file_prompt(self) -> tuple[bool, str | None]:
        save = typer.confirm("Save output to file?", default=bool(self.defaults.get("save", False)))
        path = None
        if save:
            path = typer.prompt("Output path", default=str(self.defaults.get("output_path", "output.txt")))
        return save, path

    def temperature_prompt(self) -> float:
        return float(typer.prompt("Temperature", default=str(self.defaults.get("temperature", 0.3))))

    def advanced_options_prompt(self) -> dict[str, Any]:
        chunk = typer.prompt("Chunk size", default=str(self.defaults.get("chunk_size", 8192)))
        try:
            return {"chunk_size": int(chunk)}
        except Exception:
            return {"chunk_size": int(self.defaults.get("chunk_size", 8192))}
