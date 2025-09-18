"""Rich display utilities (stubs) for CLI TUI feature.

Minimal classes so tests can import RichDisplay and ProgressTracker. Methods
raise NotImplementedError to keep the TDD gate clear.
"""
from typing import Any

__all__ = ["RichDisplay", "ProgressTracker"]


class RichDisplay:
    def __init__(self) -> None:
        pass

    def show_panel(self, title: str, content: str) -> None:
        """Show a panel with title and content in the terminal.

        Raises:
            NotImplementedError: display not implemented
        """
        raise NotImplementedError("RichDisplay.show_panel not implemented")


class ProgressTracker:
    def __init__(self) -> None:
        pass

    def start(self) -> None:
        raise NotImplementedError("ProgressTracker.start not implemented")

    def advance(self, amount: int = 1) -> None:
        raise NotImplementedError("ProgressTracker.advance not implemented")
