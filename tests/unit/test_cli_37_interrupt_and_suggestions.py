import sys

sys.path.insert(0, "src")

from hlpr.cli.interactive import InteractiveSession
from hlpr.cli.rich_display import ProgressTracker, RichDisplay
from hlpr.cli.validators import resolve_config_conflicts, suggest_file_fixes


class FakeProgress(ProgressTracker):
    def __init__(self):
        super().__init__()
        self.started = False

    def start(self, *_, **__):
        self.started = True

    def advance(self, *_, **__):
        # Simulate an interrupt on first advance
        raise KeyboardInterrupt()

    def stop(self):
        self.started = False


def test_suggest_file_fixes_empty():
    s = suggest_file_fixes("")
    assert any("Provide a non-empty file path" in x for x in s)


def test_resolve_config_conflicts_local_rich():
    opts, warnings = resolve_config_conflicts({"provider": "local", "output_format": "rich"})
    assert opts["output_format"] == "txt"
    assert warnings


def test_interactive_run_interrupt(monkeypatch):
    display = RichDisplay()
    prog = FakeProgress()
    session = InteractiveSession(display=display, progress=prog)

    # create a temporary file path that exists for validation
    import tempfile
    with tempfile.NamedTemporaryFile() as tf:
        res = session.run(tf.name, {"steps": 1, "simulate_work": True, "provider": "local", "output_format": "txt"})
        assert res["status"] == "interrupted"
        assert res["error_type"] == "keyboard_interrupt"
