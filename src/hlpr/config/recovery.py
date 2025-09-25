"""Configuration corruption recovery system.

This module provides corruption detection, atomic recovery operations,
and user data preservation during configuration reset operations.
"""

from __future__ import annotations

import contextlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .platform import PlatformConfig


@dataclass
class RecoveryResult:
    success: bool
    action_taken: str | None = None
    details: dict | None = None


class ConfigRecovery:
    """Attempt simple recovery strategies for a config file.

    Recovery strategy (attempt order):
    1. If existing config is valid JSON, do nothing (success).
    2. If config is invalid and a valid backup exists, atomically restore backup.
    3. If no valid backup, preserve corrupted file (move to backup) and write
       platform defaults atomically.
    """

    def __init__(self, config_path: Path, backup_path: Path, logger=None):
        self.config_path = config_path
        self.backup_path = backup_path
        self.logger = logger

    def _is_valid_json(self, path: Path) -> bool:
        try:
            with open(path, encoding="utf-8") as fh:
                json.load(fh)
            return True
        except (json.JSONDecodeError, OSError):
            return False

    def _atomic_write(self, path: Path, data: str) -> None:
        # Write to a temporary file in the same directory and atomically replace
        dirpath = os.path.dirname(path)
        os.makedirs(dirpath, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=dirpath, prefix=".hlpr_tmp_")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(data)
            os.replace(tmp_path, str(path))
        finally:
            # Best-effort cleanup without hiding unexpected errors
            if os.path.exists(tmp_path):
                with contextlib.suppress(OSError):
                    os.remove(tmp_path)

    def _restore_from_backup(self) -> RecoveryResult | None:
        """Attempt to restore the config file from a valid backup.

        Returns a RecoveryResult if restoration was attempted, otherwise None.
        """
        if not (self.backup_path.exists() and self._is_valid_json(self.backup_path)):
            return None
        try:
            with open(self.backup_path, encoding="utf-8") as bf:
                backup_data = bf.read()
            self._atomic_write(self.config_path, backup_data)
            return RecoveryResult(
                success=True,
                action_taken="restored_from_backup",
                details={"backup": str(self.backup_path)},
            )
        except (OSError, json.JSONDecodeError) as e:
            if self.logger:
                with contextlib.suppress(Exception):
                    self.logger.exception("Restore from backup failed: %s", e)
            return RecoveryResult(
                success=False,
                action_taken="restore_failed",
                details={"error": str(e)},
            )

    def _preserve_corrupted(self) -> str | None:
        """Move the corrupted config to a backup path, returning the new path.

        Returns None if nothing was preserved or on failure.
        """
        if not self.config_path.exists():
            return None
        try:
            os.makedirs(os.path.dirname(self.backup_path), exist_ok=True)
            if self.backup_path.exists():
                alt = self.backup_path.with_suffix(self.backup_path.suffix + ".corrupt")
                os.replace(str(self.config_path), str(alt))
                return str(alt)
            os.replace(str(self.config_path), str(self.backup_path))
            return str(self.backup_path)
        except OSError as e:
            if self.logger:
                with contextlib.suppress(Exception):
                    self.logger.exception(
                        "Failed to preserve corrupted config file: %s", e
                    )
            return None

    def recover_config(self) -> RecoveryResult:
        preserved: str | None = None

        try:
            # Case 1: config exists and is valid
            if self.config_path.exists() and self._is_valid_json(self.config_path):
                return RecoveryResult(
                    success=True,
                    action_taken="none",
                    details={"reason": "valid_config"},
                )

            # Case 2: try restore from backup
            restored = self._restore_from_backup()
            if restored is not None:
                return restored

            # Case 3: preserve corrupted file if present
            preserved = self._preserve_corrupted()

            # Finally, write defaults
            try:
                defaults = PlatformConfig.from_defaults().to_dict().get("defaults", {})
                data = json.dumps(defaults, ensure_ascii=False, indent=2)
                self._atomic_write(self.config_path, data)
                details = {"wrote_defaults": True}
                if preserved:
                    details["preserved_corrupted_at"] = preserved
                return RecoveryResult(
                    success=True,
                    action_taken="wrote_defaults",
                    details=details,
                )
            except OSError as e:
                if self.logger:
                    with contextlib.suppress(Exception):
                        self.logger.exception("Failed to write defaults: %s", e)
                return RecoveryResult(
                    success=False,
                    action_taken="write_defaults_failed",
                    details={"error": str(e)},
                )
        except Exception as e:
            if self.logger:
                with contextlib.suppress(Exception):
                    self.logger.exception("Unexpected error in recovery: %s", e)
            return RecoveryResult(
                success=False,
                action_taken="unexpected_error",
                details={"error": str(e)},
            )
