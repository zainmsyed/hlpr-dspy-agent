"""Document model for hlpr document summarization feature."""

import tempfile
from datetime import UTC, datetime
from enum import Enum
from hashlib import sha256
from pathlib import Path
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from hlpr.config import CONFIG


class FileFormat(str, Enum):
    """Supported document file formats."""

    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"


class ProcessingState(str, Enum):
    """Document processing states."""

    NEW = "new"
    PARSING = "parsing"
    PARSED = "parsed"
    SUMMARIZING = "summarizing"
    COMPLETE = "complete"
    ERROR = "error"


class Document(BaseModel):
    """Document entity for processing and summarization.

    Represents a file that can be parsed and summarized by the hlpr system.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier")
    path: str = Field(..., description="Absolute file path")
    format: FileFormat = Field(..., description="Document file format")
    size_bytes: int = Field(..., description="File size in bytes")
    content_hash: str = Field(..., description="SHA256 hash of file content")
    extracted_text: str | None = Field(
        default=None,
        description="Raw extracted text content",
    )
    summary: str | None = Field(default=None, description="Generated summary")
    key_points: list[str] = Field(
        default_factory=list,
        description="Extracted key points",
    )
    processing_time_ms: int | None = Field(
        default=None,
        description="Processing time in milliseconds",
    )
    state: ProcessingState = Field(
        default=ProcessingState.NEW,
        description="Current processing state",
    )
    error_message: str | None = Field(
        default=None,
        description="Error message if processing failed",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Last update timestamp",
    )

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Validate that the file path exists and is readable."""
        path = Path(v)
        if not path.exists():
            msg = f"File does not exist: {v}"
            raise ValueError(msg)
        if not path.is_file():
            msg = f"Path is not a file: {v}"
            raise ValueError(msg)
        if not path.stat().st_size > 0:
            msg = f"File is empty: {v}"
            raise ValueError(msg)

        # Prevent path traversal / ensure file is inside workspace or
        # system temp directory
        workspace_root = Path.cwd().resolve()
        resolved = path.resolve()

        # Allow files in workspace or system temp directory (cross-platform)
        try:
            is_in_workspace = resolved.is_relative_to(workspace_root)
        except AttributeError:
            # Older Python versions may not have is_relative_to
            is_in_workspace = str(resolved).startswith(str(workspace_root))

        system_temp = Path(tempfile.gettempdir()).resolve()
        try:
            resolved.relative_to(system_temp)
            is_in_temp = True
        except ValueError:
            # Not relative to temp directory
            is_in_temp = False

        if not (is_in_workspace or is_in_temp):
            msg = f"File path is outside of allowed workspace: {v}"
            raise ValueError(msg)

        return str(path.absolute())

    @field_validator("size_bytes")
    @classmethod
    def validate_size(cls, v: int) -> int:
        """Validate file size is within acceptable limits."""
        max_size = CONFIG.max_file_size
        if v <= 0:
            msg = "File size must be greater than 0"
            raise ValueError(msg)
        if v > max_size:
            msg = f"File size exceeds maximum limit of {max_size} bytes"
            raise ValueError(msg)
        return v

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: FileFormat, info) -> FileFormat:
        """Validate that format matches file extension."""
        if "path" in info.data:
            path = Path(info.data["path"])
            expected_format = path.suffix.lower().lstrip(".")
            if expected_format != v.value:
                msg = (
                    f"Format {v.value} does not match file extension {expected_format}"
                )
                raise ValueError(msg)
        return v

    @field_validator("content_hash")
    @classmethod
    def validate_hash(cls, v: str) -> str:
        """Validate content hash is valid SHA256."""
        if len(v) != 64:
            msg = "Content hash must be 64 characters (SHA256)"
            raise ValueError(msg)
        try:
            int(v, 16)
        except ValueError as err:
            msg = "Content hash must be valid hexadecimal"
            raise ValueError(msg) from err
        return v

    @classmethod
    def from_file(cls, file_path: str | Path) -> "Document":
        """Create a Document instance from a file path.

        Args:
            file_path: Path to the document file

        Returns:
            Document instance with computed hash and metadata
        """
        path = Path(file_path).absolute()

        # Compute hash in streaming manner to avoid loading entire file
        hasher = sha256()
        size = 0
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                size += len(chunk)
                hasher.update(chunk)
        content_hash = hasher.hexdigest()

        # Determine format from extension
        extension = path.suffix.lower().lstrip(".")
        try:
            format_enum = FileFormat(extension)
        except ValueError as err:
            msg = f"Unsupported file format: {extension}"
            raise ValueError(msg) from err

        return cls(
            path=str(path),
            format=format_enum,
            size_bytes=size,
            content_hash=content_hash,
        )

    def update_state(
        self,
        new_state: ProcessingState,
        error_message: str | None = None,
    ) -> None:
        """Update the document's processing state.

        Args:
            new_state: New processing state
            error_message: Error message if state is ERROR
        """
        self.state = new_state
        self.error_message = error_message
        self.updated_at = datetime.now(tz=UTC)

    def set_summary(
        self,
        summary: str,
        key_points: list[str],
        processing_time_ms: int,
    ) -> None:
        """Set the document's summary and related data.

        Args:
            summary: Generated summary text
            key_points: List of key points extracted
            processing_time_ms: Time taken to process in milliseconds
        """
        self.summary = summary
        self.key_points = key_points
        self.processing_time_ms = processing_time_ms
        self.state = ProcessingState.COMPLETE
        self.updated_at = datetime.now(tz=UTC)

    def to_dict(self) -> dict:
        """Convert document to dictionary representation."""
        return {
            "id": str(self.id),
            "path": self.path,
            "format": self.format.value,
            "size_bytes": self.size_bytes,
            "content_hash": self.content_hash,
            "summary": self.summary,
            "key_points": self.key_points,
            "processing_time_ms": self.processing_time_ms,
            "state": self.state.value,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
