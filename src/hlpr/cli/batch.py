"""Batch processing utilities (stubs) for CLI TUI feature."""
from typing import Iterable, List


class BatchProcessor:
    def __init__(self, workers: int = 2) -> None:
        self.workers = workers

    def process_files(self, paths: Iterable[str]) -> List[dict]:
        """Process files in parallel (stub) and return results."""
        return [{"path": p, "status": "stub"} for p in paths]
