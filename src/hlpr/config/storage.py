"""Shared configuration constants for organized storage behavior."""

from __future__ import annotations

# Minimum number of free bytes required before writing into organized storage.
# Set to 1 MiB by default; callers may override via preferences or CLI flags.
DEFAULT_MIN_FREE_BYTES = 1 * 1024 * 1024

# Maximum allowed characters for the sanitized filename stem (without extension).
# Keeps generated filenames portable across filesystems (<= 255 bytes).
MAX_FILENAME_STEM_LENGTH = 120

# Characters outside this allowlist will be replaced with an underscore during
# filename sanitization to avoid traversal and filesystem incompatibilities.
SAFE_FILENAME_PATTERN = r"[^A-Za-z0-9_.-]"
