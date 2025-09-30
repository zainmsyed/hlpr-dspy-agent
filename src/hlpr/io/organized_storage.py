from __future__ import annotations

import os
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4

from hlpr.config.storage import (
    DEFAULT_MIN_FREE_BYTES,
    MAX_FILENAME_STEM_LENGTH,
    SAFE_FILENAME_PATTERN,
)
from hlpr.exceptions import StorageError

SAFE_FILENAME_REGEX = re.compile(SAFE_FILENAME_PATTERN)


@dataclass
class OrganizedStorage:
    base_directory: Path = field(default_factory=Path.cwd)
    # Store summaries under the repository root by default to avoid
    # creating a nested `hlpr/hlpr/summaries/...` path when the project
    # root already contains the package directory. This places saved
    # summaries at <repo-root>/summaries/documents by default.
    summaries_folder: str = "summaries/documents"
    default_format: str = "md"
    create_missing_dirs: bool = True
    # minimum free bytes required to consider storage usable (None disables check)
    min_free_bytes: int | None = DEFAULT_MIN_FREE_BYTES

    def get_organized_base(self) -> Path:
        # By default we place summaries under a top-level `hlpr/` folder to
        # match CLI expectations (e.g., <cwd>/hlpr/summaries/documents). When
        # a caller provides a custom `summaries_folder` value (explicitly),
        # preserve that exact path relative to the configured base so tests
        # which pass a custom folder (e.g., tmpdir/protected_base) behave as
        # expected.
        if self.summaries_folder == "summaries/documents":
            return self.base_directory.joinpath("hlpr", self.summaries_folder)
        return self.base_directory.joinpath(self.summaries_folder)

    def _sanitized_stem(self, document_path: str) -> str:
        stem = Path(document_path).stem
        if not stem:
            stem = Path(document_path).name or f"summary_{uuid4().hex[:8]}"
        sanitized = SAFE_FILENAME_REGEX.sub("_", stem)
        sanitized = sanitized.strip("._- ")
        if not sanitized:
            sanitized = f"summary_{uuid4().hex[:8]}"

        if len(sanitized) > MAX_FILENAME_STEM_LENGTH:
            sanitized = sanitized[:MAX_FILENAME_STEM_LENGTH]

        return sanitized

    def generate_filename(self, document_path: str, format: str | None = None) -> str:
        fmt = format or self.default_format
        stem = self._sanitized_stem(document_path)
        return f"{stem}_summary.{fmt}"

    def get_organized_path(self, document_path: str, format: str | None = None) -> Path:
        base = self.get_organized_base()
        filename = self.generate_filename(document_path, format)
        return base.joinpath(filename)

    def ensure_directory_exists(self) -> Path:
        base = self.get_organized_base()
        if not self.create_missing_dirs:
            return base

        try:
            base.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise StorageError(
                message="Permission denied creating storage directory",
                details={"path": str(base)},
            ) from e
        except OSError as e:
            # Could be disk full or other OS-level error
            raise StorageError(
                message="OS error creating storage directory",
                details={"path": str(base), "error": str(e)},
            ) from e

        # Ensure the base directory is writable by the current process
        try:
            if not os.access(str(base), os.W_OK):
                raise StorageError(
                    message="Permission denied: storage directory is not writable",
                    details={"path": str(base)},
                )
        except OSError as e:
            # If os.access fails for some reason, raise a generic storage error
            raise StorageError(
                message="Failed to validate storage directory permissions",
                details={"path": str(base)},
            ) from e

        # Disk space check: honor min_free_bytes if set
        if self.min_free_bytes is not None:
            try:
                stat = shutil.disk_usage(str(base))
                if stat.free < self.min_free_bytes:
                    raise StorageError(
                        message="Insufficient disk space for storage",
                        details={
                            "attempted_path": str(base),
                            "available_bytes": stat.free,
                            "required_bytes": self.min_free_bytes,
                        },
                    )
            except StorageError:
                raise
            except OSError:
                # If disk usage check fails for any reason, continue—don't block
                pass

        return base

    def is_path_in_organized_structure(self, path: Path) -> bool:
        try:
            base = self.get_organized_base().resolve()
            return base in path.resolve().parents or path.resolve() == base
        except OSError:
            return False
