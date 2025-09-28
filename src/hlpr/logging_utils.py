"""Small structured logging helpers for hlpr.

Provides correlation id generation and helpers to build `extra` dicts for
logger calls. Kept intentionally tiny so it can be used in CLI, API, and
library code without pulling in external structured-logging libs.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4


@dataclass
class LogContext:
    correlation_id: str


def new_context(correlation_id: str | None = None) -> LogContext:
    """Create a new LogContext with a uuid4 correlation id if not provided."""
    return LogContext(correlation_id=correlation_id or str(uuid4()))


def build_extra(
    ctx: LogContext,
    **kwargs: Any,
) -> dict[str, Any]:
    """Return an `extra` dict suitable for passing to Python logging calls.

    Ensures `correlation_id` is always present and copies through provided
    metadata. Avoid adding potentially sensitive fields here.
    """
    # Merge provided metadata into the base extra dict efficiently.
    return dict({"correlation_id": ctx.correlation_id}, **kwargs)


def sanitize_filename(filename: str) -> str:
    """Return a sanitized filename (basename only) to avoid logging full paths.

    Keeps logs useful for debugging while avoiding exposing local filesystem
    layout or user home directories.
    """
    # Path() should not ordinarily raise; guard with contextlib.suppress to
    # avoid catching overly-broad exceptions.
    try:
        return Path(filename).name
    except (TypeError, ValueError):
        # Fall back to the original value if Path parsing fails for bad types
        return filename


def build_safe_extra(ctx: LogContext, **kwargs: Any) -> dict[str, Any]:
    """Build an `extra` dict and apply light sanitization to common fields.

    Currently sanitizes `file_name` to its basename and truncates long
    error strings to avoid logging large payloads.
    """
    safe = {}
    for k, v in kwargs.items():
        if k == "file_name" and isinstance(v, str):
            safe[k] = sanitize_filename(v)
        elif k == "error" and isinstance(v, str):
            # Keep error messages reasonably short
            safe[k] = v if len(v) <= 500 else (v[:500] + "...[truncated]")
        else:
            safe[k] = v

    return build_extra(ctx, **safe)
