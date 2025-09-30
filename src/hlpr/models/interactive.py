"""ProcessingOptions model for interactive guided workflow."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ProcessingOptions(BaseModel):
    """Represents collected options for processing a document."""

    provider: Literal["local", "openai", "google", "anthropic", "openrouter", "groq", "deepseek", "glm", "cohere", "mistral"] = Field(
        "local", description="LLM provider"
    )
    format: Literal["rich", "txt", "md", "json"] = Field(
        "rich", description="Output format"
    )
    temperature: float = Field(0.3, ge=0.0, le=1.0, description="Sampling temperature")
    chunk_size: int = Field(
        8192,
        gt=0,
        le=32768,
        description="Chunk size for document splitting",
    )
    save: bool = Field(False, description="Whether to save generated output to file")
    output_path: str | None = Field(
        None, description="Optional output path when save=True"
    )
    steps: int = Field(
        3, ge=1, le=100, description="Number of processing steps for progress demos"
    )
    simulate_work: bool = Field(
        False, description="Whether to simulate work with sleeps (tests disable)"
    )

    def to_cli_args(self) -> list[str]:
        """Convert options to a list of CLI args usable by other parts of the app."""
        args: list[str] = []
        args += ["--provider", self.provider]
        args += ["--format", self.format]
        args += ["--temperature", str(self.temperature)]
        args += ["--chunk-size", str(self.chunk_size)]
        if self.save:
            args += ["--save", "true"]
            if self.output_path:
                args += ["--output", self.output_path]
        # NOTE: steps is an internal UI-only setting (progress/demo). Do not
        # emit it into generated CLI invocations to avoid exposing it to
        # downstream commands or saved templates.
        return args

    @field_validator("output_path")
    @classmethod
    def validate_output_when_saving(cls, v, info):
        values = info.data
        if values.get("save") and not v:
            raise ValueError("output_path is required when save=True")
        return v

    @field_validator("temperature")
    @classmethod
    def normalize_temperature(cls, v: float) -> float:
        # limit to sensible precision for CLI representation
        return round(float(v), 3)
