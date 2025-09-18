"""Small structured logging helpers for hlpr.

Provides correlation id generation and helpers to build `extra` dicts for
logger calls. Kept intentionally tiny so it can be used in CLI, API, and
library code without pulling in external structured-logging libs.
"""
from __future__ import annotations

from dataclasses import dataclass
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
