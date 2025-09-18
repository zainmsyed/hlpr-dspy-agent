"""Interactive CLI components for guided summarization (stubs).

These are minimal placeholders used during Phase 3.1 setup so tests can import
the modules. Full implementations are added in later tasks.
"""
from typing import Any


class InteractiveSession:
    """Placeholder InteractiveSession model."""

    def __init__(self, **kwargs: Any) -> None:
        self.state = kwargs

    def run(self) -> dict:
        """Run a minimal interactive loop (stub)."""
        return {"status": "stub"}


def pick_file(prompt: str) -> str:
    """Stub for file selection."""
    return ""
