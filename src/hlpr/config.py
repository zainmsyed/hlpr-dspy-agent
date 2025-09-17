"""Centralized configuration for hlpr.

Provides a small dataclass `HlprConfig` with environment-driven defaults so
other modules can import and use a single source of truth for timeouts and
size limits.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from hlpr.config_helpers import _float_or_none, _parse_bounded_int


@dataclass(frozen=False)
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
        allowed = os.getenv("HLPR_ALLOWED_ORIGINS")
        if allowed:
            allowed_list = [s.strip() for s in allowed.split(",") if s.strip()]
            if not allowed_list:
                allowed_list = None
        else:
            allowed_list = None

        return cls(
            # Allow reasonable upper bounds to avoid accidental resource exhaustion
            max_file_size=_parse_bounded_int(
                "HLPR_MAX_FILE_SIZE",
                cls.max_file_size,
                max_value=500 * 1024 * 1024,
            ),
            max_text_length=_parse_bounded_int(
                "HLPR_MAX_TEXT_LENGTH",
                cls.max_text_length,
                max_value=50 * 1024 * 1024,
            ),
            max_memory_file_size=_parse_bounded_int(
                "HLPR_MAX_MEMORY_FILE_SIZE",
                cls.max_memory_file_size,
                max_value=200 * 1024 * 1024,
            ),
            default_timeout=_parse_bounded_int(
                "HLPR_DEFAULT_TIMEOUT",
                cls.default_timeout,
                max_value=300,
            ),
            default_fast_fail_seconds=_float_or_none(
                "HLPR_DEFAULT_FAST_FAIL_SECONDS",
                cls.default_fast_fail_seconds,
            ),
            allowed_origins=allowed_list,
        )


# Provide a module-level config instance for convenience
CONFIG = HlprConfig.from_env()
