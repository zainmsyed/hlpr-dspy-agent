"""Unit test: default interactive save behavior (press Enter -> accept defaults)

This test calls the internal _interactive_save_flow helper directly. It
monkeypatches Rich's Confirm.ask and Prompt.ask to simulate the user
confirming the save and accepting defaults. It also patches stdin.isatty to
report True so the interactive flow runs.
"""

from pathlib import Path
from types import SimpleNamespace

from hlpr.cli.summarize import _interactive_save_flow
from hlpr.models.document import Document


def test_cli_save_prompt_default(tmp_path, monkeypatch):
    # Create a dummy document file
    doc_path = tmp_path / "doc.md"
    doc_path.write_text("Hello world")

    document = Document.from_file(str(doc_path))

    # Build a minimal result object expected by the formatter
    result = SimpleNamespace(summary="This is a test summary", key_points=[])

    # Simulate TTY
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)

    # Simulate Confirm.ask -> True (accept save)
    monkeypatch.setattr("rich.prompt.Confirm.ask", lambda *_, **__: True)

    # Simulate Prompt.ask: first call (format) -> 'md', second call (output) -> default
    def prompt_ask(prompt, choices=None, default=None):
        if "Format" in str(prompt):
            return "md"
        return str(default)

    monkeypatch.setattr("rich.prompt.Prompt.ask", prompt_ask)

    # Run interactive save flow
    saved = _interactive_save_flow(document, result, "rich", None)

    assert saved is not None
    saved_path = Path(saved)
    assert saved_path.exists()
    # Basic content check
    content = saved_path.read_text()
    assert "This is a test summary" in content
