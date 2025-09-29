from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class OutputPath:
    original_document_path: str
    custom_output_path: str | None = None
    resolved_path: Path = field(default_factory=Path)
    is_organized: bool = False
    created_directories: list[Path] = field(default_factory=list)

    def validate_writable(self) -> bool:
        """Return True if the resolved path is writable (or can be created)."""
        parent = self.resolved_path.parent
        test_file = parent / ".hlpr_write_test"
        try:
            parent.mkdir(parents=True, exist_ok=True)
            with test_file.open("w", encoding="utf-8") as f:
                f.write("")
            return True
        except PermissionError:
            return False
        except OSError:
            return False
        finally:
            try:
                if test_file.exists():
                    test_file.unlink()
            except OSError:
                pass
