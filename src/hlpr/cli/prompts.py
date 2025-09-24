"""Option prompts for interactive guided workflow.

This module provides a minimal, test-friendly implementation used by
InteractiveSession. It avoids runtime input() calls in tests by returning
defaults unless overridden by injected values.
"""
from __future__ import annotations

from typing import Any

from hlpr.config.guided import (
    ALLOWED_FORMATS,
    ALLOWED_PROVIDERS,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_FORMAT,
    DEFAULT_PROVIDER,
    MAX_PROMPT_ATTEMPTS,
)
from hlpr.config.ui_strings import (
    FORMAT_EMPTY_MSG,
    FORMAT_UNSUPPORTED_TEMPLATE,
    PROVIDER_EMPTY_MSG,
    PROVIDER_UNSUPPORTED_TEMPLATE,
)

from .help_display import HelpDisplay


class OptionPrompts:
    """Provides prompt methods used by the guided interactive session.

    These methods return sensible defaults so tests can run without
    user interaction. In real usage these would use Rich/Typer prompts.
    """

    def __init__(self, defaults: dict[str, Any] | None = None) -> None:
        self.defaults = defaults or {}
        # Basic allowed values - sourced from centralized config
        self._allowed_providers = list(ALLOWED_PROVIDERS)
        self._allowed_formats = list(ALLOWED_FORMATS)
        # How many attempts an interactive implementation should allow
        self.max_attempts = int(self.defaults.get("max_attempts", MAX_PROMPT_ATTEMPTS))
        # Optional HelpDisplay instance (testable). If provided, prompts may
        # render contextual help when validation fails or when the user asks.
        self.help: HelpDisplay | None = self.defaults.get("help_display")

    def provider_prompt(self) -> str:
        """Return a provider value from defaults.

        This implementation is test-friendly: it returns the default if present
        and valid, otherwise falls back to a safe default ('local').
        Interactive prompt providers should implement retry loops using
        `validate_provider` when performing real user I/O.
        """
        candidate = str(self.defaults.get("provider", DEFAULT_PROVIDER))
        valid, _msg = self.validate_provider(candidate)
        if valid:
            return candidate
        # fallback to safe default
        # If a help display is available, show provider help to assist users
        if self.help:
            self.help.show_provider_help()
        return "local"

    def validate_provider(self, provider: str) -> tuple[bool, str]:
        """Validate provider and return (is_valid, message)."""
        if not isinstance(provider, str) or not provider:
            return False, PROVIDER_EMPTY_MSG
        if provider not in self._allowed_providers:
            return False, PROVIDER_UNSUPPORTED_TEMPLATE.format(provider=provider, allowed=", ".join(self._allowed_providers))
        return True, "ok"

    def format_prompt(self) -> str:
        candidate = str(self.defaults.get("format", DEFAULT_FORMAT))
        valid, _msg = self.validate_format(candidate)
        if valid:
            return candidate
        if self.help:
            self.help.show_format_help()
        return "rich"

    def validate_format(self, fmt: str) -> tuple[bool, str]:
        """Validate output format and return (is_valid, message)."""
        if not isinstance(fmt, str) or not fmt:
            return False, FORMAT_EMPTY_MSG
        if fmt not in self._allowed_formats:
            return False, FORMAT_UNSUPPORTED_TEMPLATE.format(fmt=fmt, allowed=", ".join(self._allowed_formats))
        return True, "ok"

    def save_file_prompt(self) -> tuple[bool, str | None]:
        save = bool(self.defaults.get("save", False))
        path = self.defaults.get("output_path")
        return save, path

    def temperature_prompt(self) -> float:
        # Validate numeric input and clamp to sensible range in test-friendly mode
        try:
            val = float(self.defaults.get("temperature", 0.3))
        except Exception:
            val = 0.3
        # enforce bounds
        if val < 0.0:
            return 0.0
        if val > 1.0:
            return 1.0
        return val

    def validate_temperature(self, temp: object) -> tuple[bool, str]:
        try:
            v = float(temp)
        except Exception:
            return False, "Temperature must be a number between 0.0 and 1.0"
        if v < 0.0 or v > 1.0:
            return False, "Temperature must be between 0.0 and 1.0"
        return True, "ok"

    def advanced_options_prompt(self) -> dict[str, Any]:
        return {
            "chunk_size": int(self.defaults.get("chunk_size", DEFAULT_CHUNK_SIZE)),
        }
