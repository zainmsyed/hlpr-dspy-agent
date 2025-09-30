"""Atomic file write helpers."""

from __future__ import annotations

import contextlib
import os
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


def atomic_write_text(path: str | Path, text: str, encoding: str = "utf-8") -> None:
    """Write text to `path` atomically.

    The function writes to a temporary file in the same directory and then
    replaces the target path using ``os.replace`` which is atomic on the same
    filesystem.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Acquire a process-level lock for the target path to reduce race
    # conditions when multiple processes try to write the same summary.
    # This uses a sidecar lock file and fcntl.flock on POSIX systems. If
    # fcntl is not available (e.g., on some Windows builds), the lock is a
    # no-op and we fall back to the existing atomic replace semantics.

    @contextmanager
    def _file_lock(target: Path) -> Iterator[None]:
        lock_path = target.parent / ("." + target.name + ".lock")
        # Open the lock file (create if missing). If it fails, fall back to
        # no-op locking.
        try:
            with open(lock_path, "a+") as fd:
                # Attempt to acquire an exclusive fcntl lock on POSIX systems.
                # If fcntl isn't available or locking fails, suppress the
                # error and continue with best-effort semantics.
                with contextlib.suppress(Exception):
                    import fcntl  # type: ignore

                    fcntl.flock(fd.fileno(), fcntl.LOCK_EX)

                try:
                    yield
                finally:
                    # Attempt to release lock; ignore failures as this is
                    # best-effort cleanup.
                    with contextlib.suppress(Exception):
                        import fcntl  # type: ignore

                        fcntl.flock(fd.fileno(), fcntl.LOCK_UN)
        except OSError:
            # Can't open lock file; no-op locking
            yield
            return

        # Best-effort: remove the lock file if it's empty
        with contextlib.suppress(OSError):
            if lock_path.exists() and lock_path.stat().st_size == 0:
                lock_path.unlink()

    # Create a temp file in the same directory to ensure os.replace is atomic
    fd, tmp_path = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    tmp_path = Path(tmp_path)
    try:
        with _file_lock(path):
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
