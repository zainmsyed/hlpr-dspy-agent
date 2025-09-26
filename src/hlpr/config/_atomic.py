"""Atomic file utilities for config operations.

Provides an atomic_write helper that writes to a same-directory temp file,
fsyncs the file and directory where supported, and sets secure permissions.
"""
from __future__ import annotations

import contextlib
import os
import tempfile
from pathlib import Path


def atomic_write(path: Path, data: str, mode: int = 0o600) -> None:
    """Atomically write `data` to `path` with secure permissions.

    Behavior:
    - Writes to a same-directory temporary file and fsyncs it (best-effort).
    - Atomically replaces the target via os.replace.
    - Attempts to fsync the containing directory (best-effort).
    - Applies file permissions to `mode` (default 0o600; best-effort).

    Args:
        path: Destination file path.
        data: String content to write.
        mode: Octal permission bits to apply to the final file.
    """
    dirpath = str(path.parent)
    os.makedirs(dirpath, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=dirpath, prefix=".hlpr_tmp_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(data)
            fh.flush()
            with contextlib.suppress(OSError, AttributeError):
                os.fsync(fh.fileno())

        os.replace(tmp_path, str(path))

        with contextlib.suppress(OSError, AttributeError):
            dir_fd = os.open(dirpath, os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)

        with contextlib.suppress(OSError):
            os.chmod(path, mode)
    finally:
        if os.path.exists(tmp_path):
            with contextlib.suppress(OSError):
                os.remove(tmp_path)
