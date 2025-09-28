"""Integration tests for CLI renderers with real data flow."""

from datetime import UTC, datetime

from hlpr.cli.models import (
    FileSelection,
    ProcessingError,
    ProcessingMetadata,
    ProcessingResult,
)
from hlpr.cli.renderers import (
    JsonRenderer,
    MarkdownRenderer,
    PlainTextRenderer,
    RichRenderer,
)


def test_renderers_with_realistic_processing_result():
    """Test all renderers with a realistic processing result."""
    # Create a realistic processing result
    file_selection = FileSelection(
        path="documents/examples/welcome_to_wrtr.md",
        size_bytes=2048,
        mime_type="text/markdown",
    )

    metadata = ProcessingMetadata(
        started_at=datetime.now(UTC),
        finished_at=datetime.now(UTC),
        duration_seconds=1.5,
    )

    result = ProcessingResult(
        file=file_selection,
        summary="This document provides a comprehensive welcome guide to the WRTR platform, "
        "covering key features, getting started steps, and best practices for users.",
        metadata=metadata,
        error=None,
    )

    # Test all renderers
    renderers = {
        "rich": RichRenderer(),
        "json": JsonRenderer(),
        "markdown": MarkdownRenderer(),
        "txt": PlainTextRenderer(),
    }

    outputs = {}

    for name, renderer in renderers.items():
        output = renderer.render(result)
        outputs[name] = output

        # Basic checks for all formats
        assert isinstance(output, str)
        assert len(output) > 0
        assert "welcome_to_wrtr.md" in output
        assert "comprehensive welcome guide" in output.lower()

    # Format-specific checks
    assert "╭" in outputs["rich"]  # Rich box drawing
    assert "│" in outputs["rich"]  # Rich box drawing

    # JSON should be parseable
    import json

    json_data = json.loads(outputs["json"])
    assert "data" in json_data
    assert "meta" in json_data

    # Markdown should have headers
    assert outputs["markdown"].startswith("# Document Summary:")
    assert "## Summary" in outputs["markdown"]

    # Plain text should have simple formatting
    assert outputs["txt"].startswith("Document Summary:")
    assert "SUMMARY:" in outputs["txt"]


def test_renderers_with_error_scenario():
    """Test all renderers handle error scenarios properly."""
    file_selection = FileSelection(
        path="documents/corrupted_file.pdf",
        size_bytes=0,
        mime_type="application/pdf",
    )

    error = ProcessingError(
        code="PARSE_ERROR",
        message="Unable to extract text from corrupted PDF file",
        details={
            "pdf_version": "1.4",
            "error_location": "page 3",
            "suggested_action": "Try re-scanning or using OCR",
        },
    )

    result = ProcessingResult(
        file=file_selection,
        summary=None,
        metadata=None,
        error=error,
    )

    renderers = [
        RichRenderer(),
        JsonRenderer(),
        MarkdownRenderer(),
        PlainTextRenderer(),
    ]

    for renderer in renderers:
        output = renderer.render(result)

        # All renderers should handle errors gracefully
        assert isinstance(output, str)
        assert len(output) > 0
        assert "corrupted_file.pdf" in output
        assert "PARSE_ERROR" in output
        assert "Unable to extract text" in output


def test_renderers_preserve_data_integrity():
    """Test that renderers preserve all important data elements."""
    # Create comprehensive test data
    file_selection = FileSelection(
        path="test/file with spaces & special-chars.txt",
        size_bytes=1536,
        mime_type="text/plain",
    )

    metadata = ProcessingMetadata(
        started_at=datetime(2025, 9, 18, 14, 30, 0, tzinfo=UTC),
        finished_at=datetime(2025, 9, 18, 14, 30, 3, tzinfo=UTC),
        duration_seconds=3.14159,
    )

    result = ProcessingResult(
        file=file_selection,
        summary="Test summary with unicode: 中文, émojis: 🚀✨, and symbols: ©®™",
        metadata=metadata,
        error=None,
    )

    for renderer in [
        RichRenderer(),
        JsonRenderer(),
        MarkdownRenderer(),
        PlainTextRenderer(),
    ]:
        output = renderer.render(result)

        # Check that special characters are preserved
        assert "file with spaces & special-chars.txt" in output
        assert "中文" in output  # Chinese characters
        assert "🚀" in output  # Emoji
        assert "émojis" in output  # Accented characters
        assert "©®™" in output  # Symbols
        assert "3.14159" in output  # Precise numbers
