
from typer.testing import CliRunner

from hlpr.cli.template_commands import app
from hlpr.models.saved_commands import SavedCommands


def test_template_save_and_list(tmp_path, monkeypatch):
    # ensure store uses a tmp path
    storage = tmp_path / "saved_commands.json"
    def _init_stub(self, path=None):
        # attach storage_path attribute for tests; ignore provided path
        self.storage_path = storage

    monkeypatch.setattr(SavedCommands, "__init__", _init_stub)
    runner = CliRunner()

    # Save a template
    result = runner.invoke(app, ["save", "hlpr summarize document /tmp/doc.md --provider local"])
    assert result.exit_code == 0
    out = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "Saved template" in result.output or "Saved template" in out.output
