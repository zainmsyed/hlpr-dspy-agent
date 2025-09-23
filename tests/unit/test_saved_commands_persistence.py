from hlpr.models.saved_commands import SavedCommands
from hlpr.models.templates import CommandTemplate


def test_saved_commands_atomic_save_and_load(tmp_path):
    # Use a temporary directory as the storage location
    storage = tmp_path / "conf"
    storage.mkdir()
    file_path = storage / "saved_commands.json"

    sc = SavedCommands(storage_path=file_path)

    # Create a simple template
    tpl = CommandTemplate.from_options(
        id="t1",
        command_template="hlpr summarize document [PASTE FILE PATH HERE] --provider local",
        options={"provider": "local"},
    )

    # Save and load
    sc.save_command(tpl)
    loaded = sc.load_commands()

    assert len(loaded) == 1
    assert loaded[0].id == "t1"
    # options are stored under the 'options' key
    assert loaded[0].model_dump()["options"]["provider"] == "local"

    # Save another and ensure replace logic works (same id should replace)
    tpl2 = CommandTemplate.from_options(
        id="t1",
        command_template="hlpr summarize document [PASTE FILE PATH HERE] --provider openai",
        options={"provider": "openai"},
    )
    sc.save_command(tpl2)
    loaded2 = sc.load_commands()
    assert len(loaded2) == 1
    assert loaded2[0].model_dump()["options"]["provider"] == "openai"
