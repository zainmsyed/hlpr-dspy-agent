"""Unit test: --save flag collision handling

Test that the --save flag uses timestamp collision handling like the
interactive save flow does.
"""

import re
from pathlib import Path
from types import SimpleNamespace

from hlpr.cli.summarize import _save_summary
from hlpr.models.document import Document
from hlpr.models.output_preferences import OutputPreferences


def test_cli_save_flag_collision_handling(tmp_path):
    """Test that --save flag creates timestamped files when target exists."""
    # Create a dummy document file
    doc_path = tmp_path / "test_doc.md"
    doc_path.write_text("Test content")

    document = Document.from_file(str(doc_path))
    result = SimpleNamespace(
        summary="Test summary", key_points=[], processing_time_ms=100
    )

    # Set up preferences to use tmp_path as base
    prefs = OutputPreferences()
    prefs.organized_base_path = tmp_path

    # First save should create the normal file
    first_save = _save_summary(document, result, "md", None, prefs)
    first_path = Path(first_save)
    assert first_path.exists()
    assert "test_doc_summary.md" in first_path.name

    # Second save should create a timestamped file (collision handling)
    second_save = _save_summary(document, result, "md", None, prefs)
    second_path = Path(second_save)
    assert second_path.exists()
    assert second_path != first_path

    # The second file should have a timestamp pattern
    assert re.search(r"_\d{8}T\d{6}", second_path.name)

    # Both files should exist
    assert first_path.exists()
    assert second_path.exists()
