"""Unit test: user declines save

Simulate Confirm.ask -> False and ensure no file is created.
"""

from types import SimpleNamespace

from hlpr.cli.summarize import _interactive_save_flow
from hlpr.models.document import Document


def test_cli_save_prompt_decline(tmp_path, monkeypatch):
    doc_path = tmp_path / "doc.md"
    doc_path.write_text("content")
    document = Document.from_file(str(doc_path))
    result = SimpleNamespace(summary="s", key_points=[])

    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("rich.prompt.Confirm.ask", lambda *_, **__: False)

    saved = _interactive_save_flow(document, result, "rich", None)
    assert saved is None
