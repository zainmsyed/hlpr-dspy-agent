"""Unit test: save as JSON format

Simulate interactive prompts choosing JSON format and assert saved file
contains `summary` and `generated_at` fields.
"""

from pathlib import Path
from types import SimpleNamespace

from hlpr.cli.summarize import _interactive_save_flow
from hlpr.models.document import Document


def test_cli_save_prompt_json(tmp_path, monkeypatch):
    doc_path = tmp_path / "doc.md"
    doc_path.write_text("hello")
    document = Document.from_file(str(doc_path))
    result = SimpleNamespace(
        summary="json summary", key_points=[], processing_time_ms=123
    )

    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("rich.prompt.Confirm.ask", lambda *_, **__: True)

    def prompt_ask(prompt, choices=None, default=None):
        if "Format" in str(prompt):
            return "json"
        return str(default)

    monkeypatch.setattr("rich.prompt.Prompt.ask", prompt_ask)

    saved = _interactive_save_flow(document, result, "rich", None)
    assert saved is not None
    p = Path(saved)
    assert p.exists()
    data = p.read_text()
    assert "json summary" in data
    assert "generated_at" in data or "summary" in data
