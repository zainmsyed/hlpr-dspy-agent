"""Batch processing utilities (stubs) for CLI TUI feature.

BatchProcessor will handle parallel file processing. For now methods raise
NotImplementedError to make the TDD gate explicit.
"""
from typing import Iterable, List

__all__ = ["BatchProcessor"]


class BatchProcessor:
    def __init__(self, workers: int = 2) -> None:
        self.workers = int(workers)

    def process_files(self, paths: Iterable[str]) -> List[dict]:
        """Process files in parallel (stub) and return results.

        Raises:
            NotImplementedError: batch processing not implemented
        """
        raise NotImplementedError("BatchProcessor.process_files not implemented")
