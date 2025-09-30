"""Unit test: StorageError mapping and friendly messages

Simulate atomic write failure and ensure StorageError is raised and
surfaceable by callers.
"""

from types import SimpleNamespace

import pytest

from hlpr.cli.summarize import _interactive_save_flow
from hlpr.models.document import Document


def test_cli_save_error_handling(tmp_path, monkeypatch):
    doc = tmp_path / "doc.md"
    doc.write_text("x")
    document = Document.from_file(str(doc))
    result = SimpleNamespace(summary="s", key_points=[], processing_time_ms=1)

    # Simulate TTY and confirm
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("rich.prompt.Confirm.ask", lambda *_, **__: True)
    monkeypatch.setattr("rich.prompt.Prompt.ask", lambda *_, **__: "md")

    # Monkeypatch atomic_write_text in the summarize module to raise OSError
    def fail_atomic(path, text):
        raise OSError("Disk full")

    monkeypatch.setattr("hlpr.cli.summarize.atomic_write_text", fail_atomic)

    from hlpr.exceptions import StorageError

    with pytest.raises(StorageError):
        _interactive_save_flow(document, result, "rich", None)
