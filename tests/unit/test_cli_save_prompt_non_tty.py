"""Unit test: non-interactive privacy-first behavior

When stdin.isatty() is False the interactive save flow should not save
unless HLPR_AUTO_SAVE is set. This test verifies both behaviors.
"""

import os
from types import SimpleNamespace

from hlpr.cli.summarize import _interactive_save_flow
from hlpr.models.document import Document


def test_cli_save_prompt_non_tty(tmp_path, monkeypatch):
    doc_path = tmp_path / "doc.md"
    doc_path.write_text("x")
    document = Document.from_file(str(doc_path))
    result = SimpleNamespace(summary="s", key_points=[], processing_time_ms=1)

    # Non-interactive (isatty False) and no env var -> no save
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    monkeypatch.delenv("HLPR_AUTO_SAVE", raising=False)
    saved = _interactive_save_flow(document, result, "rich", None)
    assert saved is None

    # With HLPR_AUTO_SAVE=true -> should save with defaults
    monkeypatch.setenv("HLPR_AUTO_SAVE", "true")
    saved2 = _interactive_save_flow(document, result, "rich", None)
    assert saved2 is not None
    assert os.path.exists(saved2)
