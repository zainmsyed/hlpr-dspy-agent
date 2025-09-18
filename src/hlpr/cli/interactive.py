"""Interactive CLI components for guided summarization (stubs).

These are minimal placeholders used during Phase 3.1 setup so tests can import
the modules. Full implementations are added in later tasks.
"""
from typing import Any, Dict

__all__ = ["InteractiveSession", "pick_file"]


class InteractiveSession:
    """Placeholder InteractiveSession model.

    Methods raise NotImplementedError to make the TDD gate explicit. Tests
    should assert the presence of these methods and that they raise until
    implemented.
    """

    def __init__(self, **kwargs: Any) -> None:
        self.state: Dict[str, Any] = dict(kwargs)

    def run(self) -> Dict[str, Any]:
        """Run a minimal interactive loop (stub).

        Raises:
            NotImplementedError: feature not yet implemented
        """
        raise NotImplementedError("InteractiveSession.run not implemented")


def pick_file(prompt: str) -> str:
    """Stub for file selection.

    Raises:
        NotImplementedError: feature not yet implemented
    """
    raise NotImplementedError("pick_file not implemented")
