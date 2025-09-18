"""Validation utilities (stubs) for CLI TUI feature.

These validators return (is_valid, message). They include minimal error
handling and are intentionally simple for initial TDD.
"""
from typing import Tuple

__all__ = ["validate_file_path", "validate_config"]


def validate_file_path(path: str) -> Tuple[bool, str]:
    """Stub file validator returns (is_valid, message).

    This performs minimal checks and will be expanded during implementation.
    """
    if not isinstance(path, str) or not path:
        return False, "empty path"
    # TODO: check filesystem existence and readability
    return True, "ok"


def validate_config(options: dict) -> Tuple[bool, str]:
    if not isinstance(options, dict):
        return False, "invalid options"
    # TODO: validate expected keys and types
    return True, "ok"
