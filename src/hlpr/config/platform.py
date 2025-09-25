"""Platform configuration constants and models.

This module provides immutable platform defaults and runtime configuration
with Pydantic validation for the hlpr configuration management system.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class PlatformDefaults(BaseModel):
    """Immutable platform-level default settings.

    - default_provider: the provider used when none is specified by the user
    - supported_providers: tuple of providers supported by the application

    The model is effectively immutable after construction — attempts to set
    attributes will raise AttributeError to match the contract tests.
    """

    default_provider: str = "local"
    supported_providers: tuple[str, ...] = Field(
        default_factory=lambda: ("local", "openai", "anthropic", "groq", "together")
    )

    # Use standard pydantic config but enforce immutability via __setattr__.
    model_config = {"frozen": False}

    def __init__(self, **data):
        super().__init__(**data)
        # Mark the instance initialized so subsequent setattr calls can be
        # rejected to provide immutability semantics.
        object.__setattr__(self, "_initialized", True)

    def __setattr__(self, name, value):
        if getattr(self, "_initialized", False):
            raise AttributeError(f"{self.__class__.__name__} is immutable")
        super().__setattr__(name, value)


class PlatformConfig(BaseModel):
    """Runtime platform configuration object.

    This model composes PlatformDefaults and provides load/save helpers that
    will be used by the ConfigLoader. Keep serialization robust to missing
    directories and validate loaded data.
    """

    defaults: PlatformDefaults

    def to_dict(self) -> dict[str, Any]:
        return {"defaults": self.defaults.model_dump()}

    @classmethod
    def from_defaults(cls, defaults: PlatformDefaults | None = None) -> PlatformConfig:
        if defaults is None:
            defaults = PlatformDefaults()
        return cls(defaults=defaults)

    def save_to_file(self, path: str) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, ensure_ascii=False, indent=2)

    @classmethod
    def load_from_file(cls, path: str) -> PlatformConfig:
        p = Path(path)
        with p.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        defaults = PlatformDefaults(**data.get("defaults", {}))
        return cls(defaults=defaults)


class ResolvedConfig(BaseModel):
    """Typed configuration object returned by ConfigLoader.

    This model provides attribute access (e.g., `result.config.provider`) used
    by integration tests and simplifies downstream consumers.
    """

    provider: str = "local"
    output_format: str = "rich"
    chunk_size: int = 8192

    def as_dict(self) -> dict[str, Any]:
        return self.model_dump()


__all__ = ["PlatformConfig", "PlatformDefaults", "ResolvedConfig"]
