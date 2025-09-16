"""Centralized configuration for hlpr.

Provides a small dataclass `HlprConfig` with environment-driven defaults so
other modules can import and use a single source of truth for timeouts and
size limits.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass


@dataclass
class HlprConfig:
    """Configuration values for hlpr.

    Values are intentionally simple and read from environment variables when
    present. Callers should use `HlprConfig.from_env()` to obtain the current
    configuration.
    """

    max_file_size: int = 100 * 1024 * 1024  # 100 MB
    max_text_length: int = 10 * 1024 * 1024  # 10 MB
    max_memory_file_size: int = 50 * 1024 * 1024  # 50 MB
    default_timeout: int = 30
    default_fast_fail_seconds: float | None = 1.0
    allowed_origins: list[str] | None = None

    @classmethod
    def from_env(cls) -> HlprConfig:
        """Create HlprConfig from environment variables.

        Recognized environment variables:
        - HLPR_MAX_FILE_SIZE (bytes)
        - HLPR_MAX_TEXT_LENGTH (bytes)
        - HLPR_MAX_MEMORY_FILE_SIZE (bytes)
        - HLPR_DEFAULT_TIMEOUT (seconds)
        - HLPR_DEFAULT_FAST_FAIL_SECONDS (float seconds or empty for None)
        - HLPR_ALLOWED_ORIGINS (comma-separated list)
        """
        logger = logging.getLogger(__name__)

        def _parse_positive_int(env_name: str, default: int) -> int:
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
            if parsed <= 0:
                logger.warning(
                    "%s=%r must be positive; using default %d",
                    env_name,
                    val,
                    default,
                )
                return default
            return parsed

        def _float_or_none(env_name: str, default: float | None) -> float | None:
            val = os.getenv(env_name)
            if not val:
                return default
            try:
                return float(val)
            except ValueError:
                logger.warning(
                    "%s=%r is not a float; using default %r",
                    env_name,
                    val,
                    default,
                )
                return default

        allowed = os.getenv("HLPR_ALLOWED_ORIGINS")
        allowed_list = [s.strip() for s in allowed.split(",")] if allowed else None

        return cls(
            max_file_size=_parse_positive_int(
                "HLPR_MAX_FILE_SIZE", cls.max_file_size,
            ),
            max_text_length=_parse_positive_int(
                "HLPR_MAX_TEXT_LENGTH", cls.max_text_length,
            ),
            max_memory_file_size=_parse_positive_int(
                "HLPR_MAX_MEMORY_FILE_SIZE", cls.max_memory_file_size,
            ),
            default_timeout=_parse_positive_int(
                "HLPR_DEFAULT_TIMEOUT", cls.default_timeout,
            ),
            default_fast_fail_seconds=_float_or_none(
                "HLPR_DEFAULT_FAST_FAIL_SECONDS", cls.default_fast_fail_seconds,
            ),
            allowed_origins=allowed_list,
        )


# Provide a module-level config instance for convenience
CONFIG = HlprConfig.from_env()
