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
    """Atomically write `data` to `path`.

    - Writes to a temp file in the same directory.
    - Flushes and fsyncs the file descriptor where possible.
    - Replaces the target with os.replace for atomic swap.
    - Attempts to fsync the containing directory.
    - Sets file permissions to `mode` where possible.
    """
    dirpath = str(path.parent)
    os.makedirs(dirpath, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=dirpath, prefix=".hlpr_tmp_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(data)
            fh.flush()
            try:
                os.fsync(fh.fileno())
            except (OSError, AttributeError):
                pass

        os.replace(tmp_path, str(path))

        try:
            dir_fd = os.open(dirpath, os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        except (OSError, AttributeError):
            pass

        try:
            os.chmod(path, mode)
        except OSError:
            pass
    finally:
        if os.path.exists(tmp_path):
            with contextlib.suppress(OSError):
                os.remove(tmp_path)
