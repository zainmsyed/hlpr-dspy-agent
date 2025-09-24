"""User preferences persistence for hlpr guided workflows.

Small, file-backed preferences manager used by guided mode and templates.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class UserPreferences:
    theme: str = "default"
    last_provider: str | None = None
    last_format: str | None = None


class PreferencesStore:
    """Simple JSON-backed store for UserPreferences.

    Default location: ~/.hlpr/user_preferences.json
    """

    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path) if path is not None else Path.home() / ".hlpr" / "user_preferences.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> UserPreferences:
        if not self.path.exists():
            return UserPreferences()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return UserPreferences(**data)
        except Exception:
            # On any error, return defaults to avoid breaking interactive flows
            return UserPreferences()

    def save(self, prefs: UserPreferences) -> None:
        data = asdict(prefs)
        self.path.write_text(json.dumps(data, default=str), encoding="utf-8")
