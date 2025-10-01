"""Default configuration values for hlpr."""

from __future__ import annotations

from pathlib import Path

DEFAULT_PROVIDER = "local"
DEFAULT_FORMAT = "rich"
DEFAULT_TEMPERATURE = 0.3
DEFAULT_MAX_TOKENS = 8192
DEFAULT_CHUNK_SIZE = 8192
MAX_PROMPT_ATTEMPTS = 3


def default_config_path() -> Path:
    """Return default config directory path (~/.hlpr)."""
    return Path.home() / ".hlpr"
