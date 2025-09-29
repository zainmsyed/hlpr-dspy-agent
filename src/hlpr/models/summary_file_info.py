from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class SummaryFileInfo:
    summary_path: Path
    original_document: str
    format: str
    created_at: datetime
    file_size_bytes: int
    used_organized_structure: bool

    @classmethod
    def from_path(cls, path: Path, original: str, used_organized: bool):
        stat = path.stat()
        return cls(
            summary_path=path,
            original_document=original,
            format=path.suffix.lstrip("."),
            created_at=datetime.fromtimestamp(stat.st_mtime),
            file_size_bytes=stat.st_size,
            used_organized_structure=used_organized,
        )
