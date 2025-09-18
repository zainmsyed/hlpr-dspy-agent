"""CLI data models for interactive summarization feature.

These models are minimal and intended for Phase 3.3. They use pydantic for
validation and will be expanded as features are implemented.
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, NonNegativeInt, field_validator, model_validator
from enum import Enum
from datetime import datetime
from pathlib import Path

__all__ = [
    "InteractiveSessionModel",
    "OutputPreferences",
    "ProcessingState",
    "ProcessingResult",
    "ProcessingMetadata",
    "ProcessingError",
    "FileSelection",
    "ProviderOption",
]


class ProviderOption(BaseModel):
    name: str
    description: Optional[str] = None
    default: bool = False


class FileSelection(BaseModel):
    path: str
    size_bytes: Optional[int] = None
    mime_type: Optional[str] = None

    @field_validator("path")
    def path_must_be_non_empty(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("path must be a non-empty string")
        return v


class ProcessingError(BaseModel):
    code: Optional[str] = None
    message: str
    details: Optional[Dict[str, Any]] = None


class ProcessingMetadata(BaseModel):
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    @field_validator("duration_seconds")
    def duration_non_negative(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("duration_seconds must be non-negative")
        return v


class ProcessingResult(BaseModel):
    file: FileSelection
    summary: Optional[str] = None
    metadata: Optional[ProcessingMetadata] = None
    error: Optional[ProcessingError] = None


class ProcessingState(BaseModel):
    total_files: NonNegativeInt = 0
    processed_files: NonNegativeInt = 0
    errors: List[ProcessingError] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_counts(self):
        if self.processed_files > self.total_files:
            raise ValueError("processed_files cannot exceed total_files")
        return self

    @property
    def completion_percentage(self) -> float:
        return (self.processed_files / self.total_files * 100) if self.total_files > 0 else 0.0

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
    max_summary_chars: Optional[int] = None

    @field_validator("max_summary_chars")
    def max_summary_non_negative(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("max_summary_chars must be positive")
        return v


class InteractiveSessionModel(BaseModel):
    session_id: Optional[str] = None
    provider: Optional[ProviderOption] = None
    preferences: OutputPreferences = Field(default_factory=OutputPreferences)
    files: List[FileSelection] = Field(default_factory=list)
    state: ProcessingState = Field(default_factory=ProcessingState)
