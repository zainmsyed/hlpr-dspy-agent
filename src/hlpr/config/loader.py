"""Configuration loading with precedence handling.

This module provides unified configuration loading from multiple sources
with proper precedence handling (user config > environment > defaults).
"""

from __future__ import annotations

import contextlib
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..config import (
    PLATFORM_DEFAULTS,
    get_env_format,
    get_env_provider,
    migrate_config,
)
from ._atomic import atomic_write
from .platform import PlatformConfig, ResolvedConfig


@dataclass
class LoadResult:
    config: ResolvedConfig
    load_time_ms: float
    source: str | None = None


class ConfigLoader:
    """Load configuration with precedence: env > file > defaults."""

    def __init__(
        self,
        config_path: Path | None = None,
        defaults: PlatformConfig | None = None,
        logger: Any | None = None,
    ):
        """Create a configuration loader.

        Args:
            config_path: Optional path to a config.json; overrides default
                location (~/.hlpr/config.json). HLPR_CONFIG_PATH takes
                precedence when set.
            defaults: Optional platform config providing default values.
            logger: Optional logger used to report non-fatal warnings
                (e.g., migration failures).
        """
        # Allow overriding via environment variable HLPR_CONFIG_PATH.
        env_path = os.environ.get("HLPR_CONFIG_PATH")
        if env_path:
            try:
                p = Path(env_path).expanduser().resolve()
            except (OSError, RuntimeError, ValueError):
                p = Path(env_path).expanduser()
            self.config_path = p
        else:
            self.config_path = config_path or Path.home() / ".hlpr" / "config.json"
        # Allow injecting a PlatformConfig instance
        self.defaults = defaults or PlatformConfig.from_defaults()
        self.logger = logger

    def _load_from_file(self) -> dict[str, Any]:
        if not self.config_path.exists():
            return {}
        try:
            import json

            with open(self.config_path, encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            # Treat decoding errors or IO issues as corruption; caller should use
            # ConfigRecovery. Don't swallow other exception types.
            return {}

    def _parse_env_value(self, v: str) -> Any:
        # Accept booleans and numbers encoded as strings
        low = v.lower()
        if low in ("true", "1", "yes", "y"):
            return True
        if low in ("false", "0", "no", "n"):
            return False
        # Try integer
        if v.isdigit() or (v.startswith("-") and v[1:].isdigit()):
            try:
                return int(v)
            except ValueError:
                # fallthrough to float/string
                pass
        # Try float
        try:
            return float(v)
        except ValueError:
            pass
        # Try JSON decode for complex values
        try:
            import json

            return json.loads(v)
        except (ValueError, TypeError):
            return v

    def _load_from_env(self) -> dict[str, Any]:
        prefix = "HLPR_"
        config: dict[str, Any] = {}
        for k, v in os.environ.items():
            if k.startswith(prefix):
                # Support nested keys using double underscore:
                # HLPR_LOG__LEVEL -> {'log': {'level': ...}}
                key = k[len(prefix):]
                parts = [p.lower() for p in key.split("__") if p]
                parsed = self._parse_env_value(v)
                target = config
                for part in parts[:-1]:
                    if part not in target or not isinstance(target[part], dict):
                        target[part] = {}
                    target = target[part]
                target[parts[-1]] = parsed
        return config

    def load_config(self) -> LoadResult:
        """Load, migrate, merge, and normalize configuration.

        Returns:
            LoadResult: Contains the resolved typed config, load duration in
            milliseconds, and an approximate source indicator ("env", "file",
            or "defaults").

        Error handling:
        - Corrupt or unreadable files are treated as empty.
        - Migration failures fall back to raw file contents and optionally
          emit a warning via the provided logger.
        """
        start = time.time()
        env_conf = self._load_from_env()
        file_conf = self._load_from_file()
        # Apply schema migrations to user config files so legacy keys are
        # transformed into the current schema before merging.
        try:
            file_conf = migrate_config(file_conf or {}) or {}
        except (ValueError, TypeError, KeyError) as e:
            # If migration fails for any reason, fall back to the raw file
            # contents to avoid crashing the loader; callers may use
            # ConfigRecovery to detect corruption.
            if self.logger is not None:
                with contextlib.suppress(Exception):
                    self.logger.warning("Config migration failed: %s", e)
            file_conf = file_conf or {}
        defaults = self.defaults.to_dict().get("defaults", {})
        # Precedence: env > file > defaults
        merged = {**defaults, **file_conf, **env_conf}

        # Normalize and provide safe fallbacks for missing values. Allow
        # env/file to set either 'provider' or legacy 'default_provider'.
        # Respect explicit env variables first, but fall back to file/defaults.
        provider_fallback = (
            merged.get("provider")
            or merged.get("default_provider")
            or defaults.get("default_provider")
            or PLATFORM_DEFAULTS.default_provider
        )
        provider = get_env_provider(provider_fallback)

        format_fallback = (
            merged.get("output_format")
            or merged.get("format")
            or defaults.get("output_format")
            or defaults.get("format")
            or PLATFORM_DEFAULTS.default_format
        )
        output_format = get_env_format(format_fallback)
        try:
            chunk_size = int(
                merged.get(
                    "chunk_size",
                    defaults.get("chunk_size", PLATFORM_DEFAULTS.default_chunk_size),
                )
            )
        except (TypeError, ValueError):
            chunk_size = defaults.get(
                "chunk_size", PLATFORM_DEFAULTS.default_chunk_size
            )

        # Normalize to typed ResolvedConfig
        resolved = ResolvedConfig(**{
            "provider": provider,
            "output_format": output_format,
            "chunk_size": chunk_size,
        })
        elapsed = (time.time() - start) * 1000.0
        # Determine source (simple heuristic)
        source = "env" if env_conf else ("file" if file_conf else "defaults")
        return LoadResult(config=resolved, load_time_ms=elapsed, source=source)

    def reset_config(self, preserve_user_data: bool = True) -> bool:
        """Reset the configuration file to platform defaults.

        If preserve_user_data is True, attempt to merge existing user keys
        that are not part of the core schema.
        """
        try:
            defaults = self.defaults.to_dict().get("defaults", {})
            existing = {}
            if self.config_path.exists():
                try:
                    import json

                    with open(self.config_path, encoding="utf-8") as fh:
                        existing = json.load(fh)
                except (json.JSONDecodeError, OSError):
                    existing = {}

            if preserve_user_data:
                # Keep keys not present in defaults
                merged = {**defaults}
                for k, v in existing.items():
                    if k not in merged:
                        merged[k] = v
            else:
                merged = defaults

            os.makedirs(self.config_path.parent, exist_ok=True)
            import json
            data = json.dumps(merged, ensure_ascii=False, indent=2)
            atomic_write(self.config_path, data)
            return True
        except OSError:
            return False
