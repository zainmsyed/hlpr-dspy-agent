"""Validation helpers for configuration values."""

from __future__ import annotations

import re
from typing import Any


def validate_temperature(value: Any) -> bool:
    """Return True if value is numeric and between 0.0 and 1.0 inclusive."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return False
    return 0.0 <= v <= 1.0


def validate_max_tokens(value: Any) -> bool:
    """Return True if value is an int > 0.

    Accepts string or numeric input and returns False for invalid types.
    """
    try:
        v = int(value)
    except (TypeError, ValueError):
        return False
    return v > 0


_KEY_RE = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z0-9\-_.]+$")


def is_valid_api_key_format(key: str) -> bool:
    """Lightweight check: must contain at least one letter and one digit,
    no spaces, and have a sensible minimum length.
    """
    if not key or not isinstance(key, str):
        return False
    if len(key) < 8:
        return False
    if " " in key:
        return False
    return bool(_KEY_RE.match(key))
