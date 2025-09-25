import asyncio
from pathlib import Path

from hlpr.models.saved_commands import SavedCommands
from hlpr.models.templates import CommandTemplate


def test_saved_commands_async_save_and_load(tmp_path):
    storage = tmp_path / "saved_commands.json"
    sc = SavedCommands(storage_path=storage)

    tpl = CommandTemplate(id="t1", command_template="echo hi", options={})

    async def run_flow():
        await sc.save_command_async(tpl)
        loaded = await sc.load_commands_async()
        assert any(c.id == "t1" for c in loaded)

        tpl2 = CommandTemplate(id="t2", command_template="echo bye", options={})
        await sc.save_command_async(tpl2)
        loaded2 = await sc.load_commands_async()
        ids = {c.id for c in loaded2}
        assert ids >= {"t1", "t2"}

    asyncio.run(run_flow())
