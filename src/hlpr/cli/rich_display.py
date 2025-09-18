"""Rich display utilities (stubs) for CLI TUI feature.

Minimal classes so tests can import RichDisplay and ProgressTracker.
"""
from typing import Any


class RichDisplay:
    def __init__(self) -> None:
        pass

    def show_panel(self, title: str, content: str) -> None:
        return None


class ProgressTracker:
    def __init__(self) -> None:
        pass

    def start(self) -> None:
        return None

    def advance(self, amount: int = 1) -> None:
        return None
