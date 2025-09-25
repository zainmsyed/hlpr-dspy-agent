"""Configuration validators for hlpr.

Enhanced validator with safer error handling and explicit provider/format checks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field, ValidationError


class _ConfigSchema(BaseModel):
    provider: str = Field("local")
    output_format: str = Field("rich")
    chunk_size: int = Field(8192, ge=1)


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[dict[str, Any]] | None = None


class ConfigValidator:
    def __init__(
        self,
        schema: Any | None = None,
        *,
        allowed_providers: list[str] | None = None,
        allowed_formats: list[str] | None = None,
    ):
        # Allow injection of a custom schema for tests later; default to the
        # in-module schema. Also accept allowed lists for provider/format checks.
        self.schema = schema or _ConfigSchema
        self.allowed_providers = (
            allowed_providers
            or [
                "local",
                "openai",
                "anthropic",
                "groq",
                "together",
            ]
        )
        self.allowed_formats = (
            allowed_formats
            or ["rich", "txt", "md", "json"]
        )

    def validate_config(self, config: dict[str, Any]) -> ValidationResult:
        errors: list[dict[str, Any]] = []
        # Basic provider/format checks first
        prov = config.get("provider")
        if prov is not None and prov not in self.allowed_providers:
            errors.append({"loc": ["provider"], "msg": f"unsupported provider: {prov}"})

        fmt = config.get("output_format") or config.get("format")
        if fmt is not None and fmt not in self.allowed_formats:
            errors.append(
                {"loc": ["output_format"], "msg": f"unsupported format: {fmt}"}
            )

        try:
            # Pydantic will coerce types when possible; if validation fails an
            # exception is raised which we convert to a structured result.
            self.schema(**config)
        except ValidationError as exc:
            for e in exc.errors():
                loc = list(e.get("loc", []))
                # Ensure we have a usable loc list
                if not loc:
                    loc = ["__root__"]
                errors.append({"loc": loc, "msg": e.get("msg")})

        if errors:
            return ValidationResult(is_valid=False, errors=errors)
        return ValidationResult(is_valid=True, errors=None)
