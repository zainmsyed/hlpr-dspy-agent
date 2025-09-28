"""Command template model used to persist and display saved command templates."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class CommandTemplate(BaseModel):
    id: str = Field(..., description="Unique identifier for the template")
    command_template: str = Field(..., description="Command string with placeholders")
    options: dict[str, Any] = Field(
        default_factory=dict,
        description="Serialized options used to create the template",
    )
    created: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def from_options(
        cls,
        id: str,
        command_template: str,
        options: dict,
    ) -> CommandTemplate:
        return cls(id=id, command_template=command_template, options=options)
