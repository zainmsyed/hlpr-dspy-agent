from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ValidationMessage:
    code: str
    message: str


class FileValidator:
    """Minimal file validation helper.

    - exists(path): return True if path exists
    - is_readable(path): return True if file exists and is readable
    - validate(path, *, must_exist=True, must_be_file=True): list[ValidationMessage]
    """

    @staticmethod
    def exists(path: str | Path) -> bool:
        return Path(path).exists()

    @staticmethod
    def is_readable(path: str | Path) -> bool:
        p = Path(path)
        try:
            return p.exists() and p.is_file() and os.access(p, os.R_OK)
        except OSError:
            return False

    @staticmethod
    def validate(
        path: str | Path,
        *,
        must_exist: bool = True,
        must_be_file: bool = True,
    ) -> list[ValidationMessage]:
        p = Path(path)
        msgs: list[ValidationMessage] = []
        if must_exist and not p.exists():
            msgs.append(
                ValidationMessage(code="not_found", message=f"Path not found: {p}")
            )
            return msgs
        if must_be_file and not p.is_file():
            msgs.append(ValidationMessage(code="not_file", message=f"Not a file: {p}"))
        try:
            if not os.access(p, os.R_OK):
                msgs.append(
                    ValidationMessage(code="not_readable", message=f"Not readable: {p}")
                )
        except OSError:
            msgs.append(
                ValidationMessage(
                    code="access_error", message=f"Access check failed: {p}"
                )
            )
        return msgs
