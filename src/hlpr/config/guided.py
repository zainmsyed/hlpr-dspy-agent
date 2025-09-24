"""Centralized constants for guided mode configuration.

Place small, well-documented constants here so multiple modules can import
shared values instead of duplicating literals across the codebase.
"""
from __future__ import annotations

from collections.abc import Sequence

ALLOWED_PROVIDERS: Sequence[str] = ("local", "openai", "anthropic", "groq", "together")
ALLOWED_FORMATS: Sequence[str] = ("rich", "txt", "md", "json")

DEFAULT_PROVIDER = "local"
DEFAULT_FORMAT = "rich"
DEFAULT_CHUNK_SIZE = 8192
MAX_PROMPT_ATTEMPTS = 3

# Help text short summary; keep in sync with help_display DEFAULT_* dicts if used.
PROVIDER_SHORT_HELP = {
    "local": "Fast offline processing. Good for small docs and privacy-sensitive data.",
    "openai": "Cloud-based, high-quality models (requires API credentials).",
    "anthropic": "Alternative cloud provider. Check rate limits and pricing.",
    "groq": "Low-latency cloud provider suitable for fast responses.",
    "together": "Shared-provider option; behavior depends on your configuration.",
}

FORMAT_SHORT_HELP = {
    "rich": "Rich terminal output with panels and color (TTY required).",
    "txt": "Plain text output, good for piping to other tools.",
    "md": "Markdown-formatted output, suitable for saving as .md files.",
    "json": "Structured JSON output for programmatic consumption.",
}
