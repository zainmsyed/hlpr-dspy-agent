import json
import os
import stat
import tempfile
import pytest
from hlpr.models.saved_commands import SavedCommands, SavedCommandsError
from hlpr.models.templates import CommandTemplate


def test_load_handles_corrupted_json(tmp_path):
    storage = tmp_path / "conf"
    storage.mkdir()
    file_path = storage / "saved_commands.json"
    # Write corrupted JSON
    file_path.write_text("{ this is not: valid json }", encoding="utf-8")

    sc = SavedCommands(storage_path=file_path)
    # load_commands should not raise; it should return an empty list on JSON error
    loaded = sc.load_commands()
    assert loaded == []


def test_save_raises_savedcommands_error_on_permission(monkeypatch, tmp_path):
    storage = tmp_path / "conf"
    storage.mkdir()
    file_path = storage / "saved_commands.json"

    sc = SavedCommands(storage_path=file_path)

    tpl = CommandTemplate.from_options(
        id="t2",
        command_template="hlpr summarize document [PASTE FILE PATH HERE] --provider local",
        options={"provider": "local"},
    )

    # Simulate permission error by monkeypatching os.replace
    def fake_replace(src, dst):
        raise PermissionError("No permission to replace file")

    monkeypatch.setattr("os.replace", fake_replace)

    with pytest.raises(SavedCommandsError):
        sc.save_command(tpl)
