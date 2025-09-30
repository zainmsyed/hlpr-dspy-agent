"""Unit test: collision handling with timestamp suffix

Create an existing file at the organized storage default path and ensure
that the interactive save flow writes a new file with a timestamp suffix.
"""

import re

from hlpr.cli.summarize import _unique_path_with_timestamp
from hlpr.models.document import Document


def test_cli_save_prompt_collision(tmp_path, monkeypatch):
    doc = tmp_path / "doc.md"
    doc.write_text("x")
    document = Document.from_file(str(doc))

    # Simulate an existing target
    from hlpr.models.output_preferences import OutputPreferences

    prefs = OutputPreferences()
    storage = prefs.to_organized_storage()
    target = storage.get_organized_path(str(document.path), "md")
    # Ensure parent exists in tmpdir
    target.parent.mkdir(parents=True, exist_ok=True)
    # Create existing file
    target.write_text("existing")

    # Now compute unique path and ensure it differs and contains timestamp
    unique = _unique_path_with_timestamp(target)
    assert unique != target
    # Timestamp pattern YYYYMMDDTHHMMSS
    assert re.search(r"_\d{8}T\d{6}", unique.name)
