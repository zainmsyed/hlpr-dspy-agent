"""Option prompts for interactive guided workflow.

This module provides a minimal, test-friendly implementation used by
InteractiveSession. It avoids runtime input() calls in tests by returning
defaults unless overridden by injected values.
"""
from __future__ import annotations

from typing import Any


class OptionPrompts:
    """Provides prompt methods used by the guided interactive session.

    These methods return sensible defaults so tests can run without
    user interaction. In real usage these would use Rich/Typer prompts.
    """

    def __init__(self, defaults: dict[str, Any] | None = None) -> None:
        self.defaults = defaults or {}

    def provider_prompt(self) -> str:
        return str(self.defaults.get("provider", "local"))

    def format_prompt(self) -> str:
        return str(self.defaults.get("format", "rich"))

    def save_file_prompt(self) -> tuple[bool, str | None]:
        save = bool(self.defaults.get("save", False))
        path = self.defaults.get("output_path")
        return save, path

    def temperature_prompt(self) -> float:
        return float(self.defaults.get("temperature", 0.3))

    def advanced_options_prompt(self) -> dict[str, Any]:
        return {
            "chunk_size": int(self.defaults.get("chunk_size", 8192)),
            "steps": int(self.defaults.get("steps", 3)),
        }
