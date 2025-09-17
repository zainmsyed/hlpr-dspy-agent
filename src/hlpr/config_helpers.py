"""Helper parsing utilities for hlpr configuration.

This module exposes small pure functions used by `HlprConfig.from_env()` so the
method remains simple and easier to lint.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def _parse_bounded_int(
    env_name: str,
    default: int,
    *,
    min_value: int = 1,
    max_value: int | None = None,
) -> int:
    """Parse a positive integer from env with optional upper bound.

    Returns the default if parsing fails or if value is outside bounds.
    """
    val = os.getenv(env_name)
    if not val:
        return default
    try:
        parsed = int(val)
    except ValueError:
        logger.warning(
            "%s=%r is not an integer; using default %d",
            env_name,
            val,
            default,
        )
        return default
    if parsed < min_value:
        logger.warning(
            "%s=%r must be >= %d; using default %d",
            env_name,
            val,
            min_value,
            default,
        )
        return default
    if max_value is not None and parsed > max_value:
        logger.warning(
            "%s=%r exceeds maximum %d; using default %d",
            env_name,
            val,
            max_value,
            default,
        )
        return default
    return parsed


def _float_or_none(env_name: str, default: float | None) -> float | None:
    """Parse a positive float from env or return default/None.

    Returns default when parsing fails or the value is non-positive.
    """
    val = os.getenv(env_name)
    if not val:
        return default
    try:
        parsed = float(val)
    except ValueError:
        logger.warning(
            "%s=%r is not a float; using default %r",
            env_name,
            val,
            default,
        )
        return default
    if parsed <= 0:
        logger.warning(
            "%s=%r must be positive; using default %r",
            env_name,
            val,
            default,
        )
        return default
    return parsed
