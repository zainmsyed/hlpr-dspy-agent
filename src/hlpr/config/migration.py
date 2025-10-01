"""Configuration migration utilities.

This module provides simple migration functions to upgrade older config
representations to the current schema. For now it's a no-op placeholder
that returns the input state.
"""

from __future__ import annotations

from typing import Any


def migrate_config_v1_to_v2(state: dict[str, Any]) -> dict[str, Any]:
    """No-op migration for now — return state unchanged.

    In future, implement transformations here.
    """
    # Placeholder: validate keys or rename fields when needed
    return state
