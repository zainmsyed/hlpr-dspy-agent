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
    # Logging controls
    include_file_paths: bool = False
    include_text_length: bool = True
    include_correlation_header: bool = True
    performance_logging: bool = True

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
            # Logging flags
            include_file_paths=(
                os.getenv("HLPR_INCLUDE_FILE_PATHS", "false").lower() == "true"
            ),
            include_text_length=(
                os.getenv("HLPR_INCLUDE_TEXT_LENGTH", "true").lower() == "true"
            ),
            include_correlation_header=(
                os.getenv("HLPR_INCLUDE_CORRELATION_HEADER", "true").lower() == "true"
            ),
            performance_logging=(
                os.getenv("HLPR_PERFORMANCE_LOGGING", "true").lower() == "true"
            ),
        )


# Provide a module-level config instance for convenience
CONFIG = HlprConfig.from_env()


# New: Platform-level constants and small compatibility helpers
@dataclass(frozen=True)
class PlatformDefaults:
    """Immutable platform constants. Kept minimal and backward-compatible.

    These values are intended as a single source of truth for CLI modules that
    need provider/format defaults or filesystem layout. Do not assume this
    replaces the existing HlprConfig; both are provided for compatibility.
    """

    # Provider defaults
    default_provider: str = "local"
    supported_providers: tuple[str, ...] = ("local", "openai", "anthropic", "groq", "together")

    # Format defaults
    default_format: str = "rich"
    supported_formats: tuple[str, ...] = ("rich", "txt", "md", "json")

    # Chunk size limits
    default_chunk_size: int = 8192
    min_chunk_size: int = 1024
    max_chunk_size: int = 32768

    # File layout
    config_dir_name: str = ".hlpr"
    config_filename: str = "config.json"
    backup_filename: str = "config.backup.json"


# Expose a module-level instance for convenience
PLATFORM_DEFAULTS = PlatformDefaults()


def get_env_provider(default: str | None = None) -> str:
    """Return configured provider from env with backward-compatible names.

    Looks for HLPR_DEFAULT_PROVIDER then HLPR_PROVIDER as a fallback.
    Falls back to the given `default` or PLATFORM_DEFAULTS.default_provider.
    """
    provider = os.getenv("HLPR_DEFAULT_PROVIDER") or os.getenv("HLPR_PROVIDER")
    return provider if provider else (default or PLATFORM_DEFAULTS.default_provider)


def get_env_format(default: str | None = None) -> str:
    """Return configured output format from env with compatibility.

    Looks for HLPR_DEFAULT_FORMAT then HLPR_FORMAT. Falls back to the
    supplied default or PLATFORM_DEFAULTS.default_format.
    """
    fmt = os.getenv("HLPR_DEFAULT_FORMAT") or os.getenv("HLPR_FORMAT")
    return fmt if fmt else (default or PLATFORM_DEFAULTS.default_format)


# Migration helper (lightweight wrapper)
from hlpr.config.migration import migrate as _migrate_config, MigrationError


def migrate_config(config_dict: dict) -> dict:
    """Migrate a config dictionary to the current schema version.

    This delegates to the migration module; kept here for convenience so
    callers may import from `hlpr.config` instead of the submodule.
    """
    return _migrate_config(config_dict)

