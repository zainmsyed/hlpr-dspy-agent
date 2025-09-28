"""Atomic file write helpers."""

from __future__ import annotations

import contextlib
import os
import tempfile
from pathlib import Path


def atomic_write_text(path: str | Path, text: str, encoding: str = "utf-8") -> None:
    """Write text to `path` atomically.

    The function writes to a temporary file in the same directory and then
    replaces the target path using ``os.replace`` which is atomic on the same
    filesystem.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Create a temp file in the same directory to ensure os.replace is atomic
    fd, tmp_path = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    tmp_path = Path(tmp_path)
    try:
        # Write bytes to the file descriptor and fsync
        with os.fdopen(fd, "wb") as f:
            b = text.encode(encoding)
            f.write(b)
            f.flush()
            os.fsync(f.fileno())

        # Atomically replace target
        tmp_path.replace(path)

        # Best-effort: fsync parent directory so directory entries are durable
        try:
            dir_fd = os.open(str(path.parent), os.O_DIRECTORY)
        except OSError:
            # Not critical; ignore if the directory cannot be opened for fsync
            dir_fd = None
        else:
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
    except Exception:
        # Clean up temp file on failure (best-effort)
        with contextlib.suppress(OSError, FileNotFoundError):
            tmp_path.unlink(missing_ok=True)
        raise
