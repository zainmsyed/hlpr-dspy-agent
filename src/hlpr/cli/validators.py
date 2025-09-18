"""Validation utilities for the CLI TUI feature.

These helpers return (is_valid, message). They perform filesystem checks and
basic schema checks for CLI-provided configuration options.
"""
import os
from collections.abc import Iterable
from pathlib import Path

__all__ = ["validate_config", "validate_file_path"]


def validate_file_path(path: str) -> tuple[bool, str]:
    """Validate that `path` refers to a readable file.

    Returns (True, "ok") when valid, otherwise (False, <error message>).
    """
    if not isinstance(path, str) or not path:
        return False, "empty or invalid path"

    p = Path(path)
    if not p.exists():
        return False, "path does not exist"

    if not p.is_file():
        return False, "path is not a file"

    try:
        if not os.access(path, os.R_OK):
            return False, "file is not readable"
    except OSError:
        return False, "file accessibility could not be determined"

    return True, "ok"


def validate_config(
    options: dict[str, object],
    *,
    allowed_providers: Iterable[str] = ("local", "openai", "anthropic"),
    allowed_output_formats: Iterable[str] = (
        "rich",
        "txt",
        "md",
        "json",
    ),
    required_keys: Iterable[str] = ("provider", "output_format"),
) -> tuple[bool, str]:
    """Validate a simple CLI config/options mapping.

    Checks that required keys are present and that provider/output_format are
    in allowed values. Returns (True, "ok") on success.
    """
    if not isinstance(options, dict):
        return False, "options must be a dict"

    for key in required_keys:
        if key not in options:
            return False, f"missing required option: {key}"

    provider = options.get("provider")
    if provider not in allowed_providers:
        return False, f"unsupported provider: {provider}"

    ofmt = options.get("output_format")
    if ofmt not in allowed_output_formats:
        return False, f"unsupported output_format: {ofmt}"

    return True, "ok"
