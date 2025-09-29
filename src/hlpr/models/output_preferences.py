from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from hlpr.config.storage import DEFAULT_MIN_FREE_BYTES


@dataclass
class OutputPreferences:
    use_organized_storage: bool = True
    organized_base_path: Path | None = None
    default_summary_format: str = "md"
    create_directories_automatically: bool = True
    # Minimum free bytes required for organized storage; None disables check
    min_free_bytes: int | None = DEFAULT_MIN_FREE_BYTES

    def effective_base(self) -> Path:
        if self.organized_base_path:
            return self.organized_base_path
        return Path.cwd()

    def to_organized_storage(self):
        """Return an OrganizedStorage configured from these preferences."""
        from hlpr.io.organized_storage import OrganizedStorage

        return OrganizedStorage(
            base_directory=self.effective_base(),
            create_missing_dirs=self.create_directories_automatically,
            default_format=self.default_summary_format,
            min_free_bytes=self.min_free_bytes,
        )
