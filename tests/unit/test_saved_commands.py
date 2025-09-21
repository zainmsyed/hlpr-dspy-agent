import json

from hlpr.models.saved_commands import SavedCommands
from hlpr.models.templates import CommandTemplate


def test_saved_commands_write_and_load(tmp_path):
    storage = tmp_path / "saved.json"
    saver = SavedCommands(storage_path=storage)
    t = CommandTemplate.from_options(id="1", command_template="a b c", options={})
    saver.save_command(t)
    assert storage.exists()
    data = json.loads(storage.read_text())
    assert isinstance(data, list)
    assert data[0]["id"] == "1"
