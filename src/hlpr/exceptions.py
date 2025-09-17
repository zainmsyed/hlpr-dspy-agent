"""Domain-specific exceptions for hlpr.

Defines a small hierarchy of exceptions to improve error handling and
make API responses more structured and machine-readable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from starlette import status


class HlprError(Exception):
    """Base class for hlpr domain errors.

    Subclasses may be dataclasses that define `message`, `code`, and
    `details`. This base class provides helpers for consistent serialization
    and an HTTP status mapping.
    """

    def __str__(self) -> str:  # pragma: no cover - trivial
        # Prefer 'message' attr when present for nicer stringification
        return getattr(self, "message", super().__str__())

    def to_dict(self) -> dict[str, Any]:
        # Default representation if subclass doesn't implement its own
        return {
            "error": str(self),
            "error_code": getattr(self, "code", "HLPR_ERROR"),
            "details": getattr(self, "details", None),
        }

    def status_code(self) -> int:
        return status.HTTP_500_INTERNAL_SERVER_ERROR


@dataclass
class DocumentProcessingError(HlprError):
    message: str
    code: str = "DOCUMENT_PROCESSING_ERROR"
    details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"error": self.message, "error_code": self.code, "details": self.details}

    def status_code(self) -> int:
        return status.HTTP_400_BAD_REQUEST


@dataclass
class SummarizationError(RuntimeError, HlprError):
    message: str
    code: str = "SUMMARIZATION_ERROR"
    details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"error": self.message, "error_code": self.code, "details": self.details}

    def status_code(self) -> int:
        return status.HTTP_422_UNPROCESSABLE_ENTITY


@dataclass
class ConfigurationError(HlprError):
    message: str
    code: str = "CONFIGURATION_ERROR"
    details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"error": self.message, "error_code": self.code, "details": self.details}

    def status_code(self) -> int:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
