"""Configuration loading with precedence handling.

This module provides unified configuration loading from multiple sources
with proper precedence handling (user config > environment > defaults).
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .platform import PlatformConfig, ResolvedConfig


@dataclass
class LoadResult:
    config: ResolvedConfig
    load_time_ms: float
    source: str | None = None


class ConfigLoader:
    """Load configuration with normalized values and a typed result.

    Precedence (higher wins): env > file > defaults
    """

    def __init__(
        self,
        config_path: Path | None = None,
        defaults: PlatformConfig | None = None,
    ):
        self.config_path = config_path or Path.home() / ".hlpr" / "config.json"
        # Allow injecting a PlatformConfig instance
        self.defaults = defaults or PlatformConfig.from_defaults()

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
        return v

    def _load_from_env(self) -> dict[str, Any]:
        prefix = "HLPR_"
        config: dict[str, Any] = {}
        for k, v in os.environ.items():
            if k.startswith(prefix):
                key = k[len(prefix):].lower()
                config[key] = self._parse_env_value(v)
        return config

    def load_config(self) -> LoadResult:
        start = time.time()
        env_conf = self._load_from_env()
        file_conf = self._load_from_file()
        defaults = self.defaults.to_dict().get("defaults", {})
        # Precedence: env > file > defaults
        merged = {**defaults, **file_conf, **env_conf}

        # Normalize and provide safe fallbacks for missing values
        # Allow env/file to set either 'provider' or legacy 'default_provider'
        provider = (
            merged.get("provider")
            or merged.get("default_provider")
            or defaults.get("default_provider")
            or "local"
        )
        output_format = (
            merged.get("output_format")
            or merged.get("format")
            or defaults.get("output_format")
            or defaults.get("format")
            or "rich"
        )
        try:
            chunk_size = int(
                merged.get("chunk_size", defaults.get("chunk_size", 8192))
            )
        except (TypeError, ValueError):
            chunk_size = defaults.get("chunk_size", 8192)

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

            with open(self.config_path, "w", encoding="utf-8") as fh:
                json.dump(merged, fh, ensure_ascii=False, indent=2)
            return True
        except OSError:
            return False
