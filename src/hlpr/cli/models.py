"""CLI data models for interactive summarization feature.

These models are minimal and intended for Phase 3.3. They use pydantic for
validation and will be expanded as features are implemented.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, NonNegativeInt, field_validator, model_validator

__all__ = [
    "FileSelection",
    "InteractiveSessionModel",
    "OutputPreferences",
    "ProcessingError",
    "ProcessingMetadata",
    "ProcessingResult",
    "ProcessingState",
    "ProviderOption",
]


class ProviderOption(BaseModel):
    name: str
    description: str | None = None
    default: bool = False


class FileSelection(BaseModel):
    path: str
    size_bytes: int | None = None
    mime_type: str | None = None

    @field_validator("path")
    @classmethod
    def path_must_be_non_empty(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            msg = "path must be a non-empty string"
            raise ValueError(msg)
        return v


class ProcessingError(BaseModel):
    code: str | None = None
    message: str
    details: dict[str, Any] | None = None


class ProcessingMetadata(BaseModel):
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration_seconds: float | None = None
    provider: str | None = None
    key_points: list[str] | None = None
    hallucinations: list[str] | None = None

    @field_validator("duration_seconds")
    @classmethod
    def duration_non_negative(cls, v: float | None) -> float | None:
        if v is not None and v < 0:
            msg = "duration_seconds must be non-negative"
            raise ValueError(msg)
        return v


class ProcessingResult(BaseModel):
    file: FileSelection
    summary: str | None = None
    metadata: ProcessingMetadata | None = None
    error: ProcessingError | None = None


class ProcessingState(BaseModel):
    total_files: NonNegativeInt = 0
    processed_files: NonNegativeInt = 0
    errors: list[ProcessingError] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_counts(self):
        if self.processed_files > self.total_files:
            msg = "processed_files cannot exceed total_files"
            raise ValueError(msg)
        return self

    @property
    def completion_percentage(self) -> float:
        if self.total_files > 0:
            return float(self.processed_files / self.total_files * 100)
        return 0.0

    @property
    def is_complete(self) -> bool:
        return self.total_files > 0 and self.processed_files >= self.total_files


class OutputFormat(str, Enum):
    RICH = "rich"
    JSON = "json"
    MARKDOWN = "md"
    TEXT = "txt"


class OutputPreferences(BaseModel):
    format: OutputFormat = Field(default=OutputFormat.RICH, description="Output format")
    include_metadata: bool = True
    max_summary_chars: int | None = None

    @field_validator("max_summary_chars")
    @classmethod
    def max_summary_non_negative(cls, v: int | None) -> int | None:
        if v is not None and v <= 0:
            msg = "max_summary_chars must be positive"
            raise ValueError(msg)
        return v


class InteractiveSessionModel(BaseModel):
    session_id: str | None = None
    provider: ProviderOption | None = None
    preferences: OutputPreferences = Field(default_factory=OutputPreferences)
    files: list[FileSelection] = Field(default_factory=list)
    state: ProcessingState = Field(default_factory=ProcessingState)
