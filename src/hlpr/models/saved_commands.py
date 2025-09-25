"""Manager for saving and loading command templates."""
from __future__ import annotations

import asyncio
import contextlib
import json
import os
import tempfile
from pathlib import Path

from hlpr.config import CONFIG
from hlpr.models.templates import CommandTemplate


class SavedCommandsError(Exception):
    """Raised when saving or loading saved commands fails.

    Applies to non-recoverable persistence/serialization errors.
    """


class SavedCommands:
    """Simple file-backed manager for command templates.

    Stores templates as a JSON array in the workspace .hlpr directory by default.
    """

    def __init__(self, storage_path: str | Path | None = None) -> None:
        if storage_path is not None:
            self.storage_path = Path(storage_path)
        else:
            base = (
                Path(CONFIG.user_config_dir)
                if getattr(CONFIG, "user_config_dir", None)
                else Path.cwd() / ".hlpr"
            )
            self.storage_path = base / "saved_commands.json"
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def save_command(self, template: CommandTemplate) -> None:
        # perform read-modify-write via atomic write to avoid partial writes
        commands = self.load_commands()
        commands = [c for c in commands if c.id != template.id]
        commands.append(template)
        self._atomic_write(commands)

    def load_commands(self) -> list[CommandTemplate]:
        if not self.storage_path.exists():
            return []
        try:
            raw = json.loads(self.storage_path.read_text(encoding="utf-8"))
            return [CommandTemplate(**r) for r in raw]
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            return []

    def _write(self, commands: list[CommandTemplate]) -> None:
        raw = [c.model_dump() for c in commands]
        self.storage_path.write_text(json.dumps(raw, default=str), encoding="utf-8")

    def _atomic_write(self, commands: list[CommandTemplate]) -> None:
        raw = [c.model_dump() for c in commands]
        # write to a temp file in the same directory then rename
        dirpath = self.storage_path.parent
        fd, tmp = tempfile.mkstemp(dir=dirpath)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(json.dumps(raw, default=str))
            os.replace(tmp, self.storage_path)
        except (OSError, PermissionError) as exc:
            # Attempt to clean up the temp file, then raise a domain-specific error
            with contextlib.suppress(Exception):
                os.remove(tmp)
            raise SavedCommandsError(
                f"Failed to write saved commands to {self.storage_path}: {exc}"
            ) from exc
        except Exception as exc:  # pragma: no cover - defensive
            with contextlib.suppress(Exception):
                os.remove(tmp)
            raise SavedCommandsError(
                f"Unexpected failure when writing saved commands: {exc}"
            ) from exc

    # ---- Async helpers (use asyncio.to_thread to avoid adding aiofiles) ----
    async def save_command_async(self, template: CommandTemplate) -> None:
        """Async wrapper for save_command.

        Offloads the synchronous save to a thread to avoid blocking an event loop.
        """
        await asyncio.to_thread(self.save_command, template)

    async def load_commands_async(self) -> list[CommandTemplate]:
        """Async wrapper for load_commands.

        Returns the list of CommandTemplate instances.
        """
        return await asyncio.to_thread(self.load_commands)

    async def _atomic_write_async(self, commands: list[CommandTemplate]) -> None:
        """Async wrapper around the atomic write helper."""
        await asyncio.to_thread(self._atomic_write, commands)
