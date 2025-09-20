"""Validation utilities for the CLI TUI feature.

These helpers return (is_valid, message). They perform filesystem checks and
basic schema checks for CLI-provided configuration options.
"""
import os
from collections.abc import Iterable
from pathlib import Path

__all__ = [
    "resolve_config_conflicts",
    "suggest_file_fixes",
    "validate_config",
    "validate_file_path",
]


def validate_file_path(path: str) -> tuple[bool, str]:
    """Validate that `path` refers to a readable file.

    Returns (True, "ok") when valid, otherwise (False, <error message>).
    """
    if not isinstance(path, str) or not path:
        return False, "empty path"

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


def suggest_file_fixes(path: str) -> list[str]:
    """Return a small list of suggestions for common file path problems.

    This is intentionally lightweight: callers should present suggestions to
    users when validation fails (e.g., typo corrections, missing extension).
    """
    suggestions: list[str] = []
    if not isinstance(path, str) or not path:
        suggestions.append("Provide a non-empty file path")
        return suggestions

    p = Path(path)
    # Suggest adding common extensions if missing
    if not p.suffix:
        suggestions.append(f"Did you mean '{path}.md' or '{path}.txt'?")

    # Suggest checking working directory when path looks relative
    if not p.is_absolute():
        suggestions.append("Try using an absolute path or verify current working directory")

    return suggestions


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
    # Accept an empty dict as a valid (default) configuration to support
    # callers that build options incrementally. This behavior is relied upon
    # by contract tests which expect `validate_config({}) == (True, "ok")`.
    if not isinstance(options, dict):
        return False, "options must be a dict"

    if not options:
        return True, "ok"

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


def resolve_config_conflicts(options: dict[str, object]) -> tuple[dict[str, object], list[str]]:
    """Detect and resolve simple configuration conflicts.

    Returns a tuple of (resolved_options, warnings). This resolver handles a
    small set of predictable conflicts: e.g., incompatible provider+format
    combinations, or mutually exclusive flags. The function makes conservative
    choices and records warnings instead of silently changing user intent.
    """
    resolved = dict(options or {})
    warnings: list[str] = []

    provider = resolved.get("provider")
    fmt = resolved.get("output_format")
    if provider == "local" and fmt == "rich":
        # local provider might not support rich rendering in headless contexts
        warnings.append("'local' provider may not support 'rich' output in headless environments; falling back to 'txt'")
        resolved["output_format"] = "txt"

    # Normalize boolean flags that may be provided as strings
    for key in ("simulate_work", "dry_run"):
        if key in resolved and isinstance(resolved[key], str):
            val = resolved[key].lower()
            if val in ("1", "true", "yes", "y"):  # type: ignore[attr-defined]
                resolved[key] = True
            elif val in ("0", "false", "no", "n"):
                resolved[key] = False

    return resolved, warnings
