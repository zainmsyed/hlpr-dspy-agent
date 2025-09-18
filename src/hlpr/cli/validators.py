"""Validation utilities (stubs) for CLI TUI feature."""
from typing import Tuple


def validate_file_path(path: str) -> Tuple[bool, str]:
    """Stub file validator returns (is_valid, message)."""
    if not path:
        return False, "empty path"
    return True, "ok"


def validate_config(options: dict) -> Tuple[bool, str]:
    if not isinstance(options, dict):
        return False, "invalid options"
    return True, "ok"
