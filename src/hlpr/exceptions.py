"""Domain-specific exceptions for hlpr.

Defines a small hierarchy of exceptions to improve error handling and
make API responses more structured and machine-readable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from starlette import status


@dataclass
class HlprError(Exception):
    """Base domain error for hlpr.

    Use as a dataclass so subclasses can declare message/code/details
    without repeating serialization logic.
    """
    message: str | None = None
    code: str = "HLPR_ERROR"
    details: dict[str, Any] | None = None

    def __str__(self) -> str:  # pragma: no cover - trivial
        return str(self.message) if self.message is not None else super().__str__()

    def to_dict(self) -> dict[str, Any]:
        return {"error": str(self), "error_code": self.code, "details": self.details}

    def status_code(self) -> int:
        return status.HTTP_500_INTERNAL_SERVER_ERROR


@dataclass
class DocumentProcessingError(HlprError):
    code: str = "DOCUMENT_PROCESSING_ERROR"

    def status_code(self) -> int:
        return status.HTTP_400_BAD_REQUEST


@dataclass
class SummarizationError(HlprError, RuntimeError):
    code: str = "SUMMARIZATION_ERROR"

    def status_code(self) -> int:
        return status.HTTP_422_UNPROCESSABLE_ENTITY
        # Adding RuntimeError as a superclass


@dataclass
class ValidationError(HlprError):
    """Raised for user/input validation errors (non-Pydantic field validation).

    Note: keep Pydantic field validators raising built-in ValueError so
    Pydantic reports proper field errors. Use this ValidationError for
    higher-level checks where a domain-level validation error is clearer.
    """
    code: str = "VALIDATION_ERROR"

    def status_code(self) -> int:
        return status.HTTP_400_BAD_REQUEST


@dataclass
class ConfigurationError(HlprError):
    code: str = "CONFIGURATION_ERROR"

    def status_code(self) -> int:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
