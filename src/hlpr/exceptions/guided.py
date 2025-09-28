"""Custom exceptions for guided interactive workflows.

Keep a small, well-documented hierarchy so callers can catch
interactive-specific errors separately from other errors.
"""

from __future__ import annotations


class GuidedError(Exception):
    """Base class for all guided-mode related exceptions."""

    pass


class ValidationError(GuidedError):
    """Raised when user-provided input fails validation."""


class UserAbortError(GuidedError):
    """Raised when a user explicitly aborts an interactive operation."""


class IOAccessError(GuidedError):
    """Raised when file/system access fails in a way relevant to guided workflows."""


# Backwards-compatible alias (older code may reference UserAbort)
UserAbort = UserAbortError
