"""Unit tests for CLI renderers."""

import json
from datetime import UTC, datetime

import pytest
from rich.console import Console

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


@pytest.fixture
def sample_processing_result():
    """Create a sample ProcessingResult for testing."""
    file_selection = FileSelection(
        path="test_document.txt",
        size_bytes=1024,
        mime_type="text/plain",
    )

    metadata = ProcessingMetadata(
        started_at=datetime(2025, 1, 1, 10, 0, 0, tzinfo=UTC),
        finished_at=datetime(2025, 1, 1, 10, 0, 5, tzinfo=UTC),
        duration_seconds=5.0,
    )

    return ProcessingResult(
        file=file_selection,
        summary="This is a test document with sample content for testing the renderers.",
        metadata=metadata,
        error=None,
    )


@pytest.fixture
def error_processing_result():
    """Create a ProcessingResult with an error for testing."""
    file_selection = FileSelection(path="error_document.txt")

    error = ProcessingError(
        code="E001",
        message="Failed to process document",
        details={"line": 42, "reason": "Invalid format"},
    )

    return ProcessingResult(
        file=file_selection,
        summary=None,
        metadata=None,
        error=error,
    )


class TestRichRenderer:
    """Test the RichRenderer class."""

    def test_render_processing_result(self, sample_processing_result):
        """Test rendering a ProcessingResult with RichRenderer."""
        renderer = RichRenderer()
        output = renderer.render(sample_processing_result)

        # Check that key elements are present in output
        assert "test_document.txt" in output
        assert "This is a test document" in output
        assert "Processing Metadata" in output
        assert "Duration Seconds" in output

    def test_render_error_result(self, error_processing_result):
        """Test rendering an error result with RichRenderer."""
        renderer = RichRenderer()
        output = renderer.render(error_processing_result)

        assert "Error" in output
        assert "E001" in output
        assert "Failed to process document" in output
        assert "line" in output  # From details

    def test_render_result_list(
        self, sample_processing_result, error_processing_result
    ):
        """Test rendering a list of results."""
        renderer = RichRenderer()
        results = [sample_processing_result, error_processing_result]
        output = renderer.render(results)

        assert "Processing Results (2 files)" in output
        assert "Result 1:" in output
        assert "test_document.txt" in output
        assert "error_document.txt" in output

    def test_render_dict(self):
        """Test rendering a generic dictionary."""
        renderer = RichRenderer()
        data = {"status": "success", "count": 5, "message": "All done"}
        output = renderer.render(data)

        assert "Results" in output
        assert "status" in output
        assert "success" in output

    def test_console_injection(self, sample_processing_result):
        """Test that console can be injected for testing."""
        console = Console(record=True, width=80)
        renderer = RichRenderer(console=console)

        # This should not raise an error
        output = renderer.render(sample_processing_result)
        assert isinstance(output, str)
        assert len(output) > 0


class TestJsonRenderer:
    """Test the JsonRenderer class."""

    def test_render_processing_result(self, sample_processing_result):
        """Test rendering a ProcessingResult as JSON."""
        renderer = JsonRenderer()
        output = renderer.render(sample_processing_result)

        # Parse the JSON to ensure it's valid
        data = json.loads(output)

        assert "data" in data
        assert "meta" in data
        assert data["meta"]["renderer"] == "JsonRenderer"
        assert "timestamp" in data["meta"]

        # Check that the processing result data is present
        result_data = data["data"]
        assert result_data["file"]["path"] == "test_document.txt"
        assert "This is a test document" in result_data["summary"]

    def test_render_error_result(self, error_processing_result):
        """Test rendering an error result as JSON."""
        renderer = JsonRenderer()
        output = renderer.render(error_processing_result)

        data = json.loads(output)
        result_data = data["data"]

        assert result_data["error"]["code"] == "E001"
        assert result_data["error"]["message"] == "Failed to process document"
        assert result_data["error"]["details"]["line"] == 42

    def test_render_result_list(
        self, sample_processing_result, error_processing_result
    ):
        """Test rendering a list of results as JSON."""
        renderer = JsonRenderer()
        results = [sample_processing_result, error_processing_result]
        output = renderer.render(results)

        data = json.loads(output)
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 2

    def test_custom_formatting_options(self, sample_processing_result):
        """Test JsonRenderer with custom formatting options."""
        renderer = JsonRenderer(indent=None, sort_keys=False)
        output = renderer.render(sample_processing_result)

        # Should be valid JSON even with no indentation
        data = json.loads(output)
        assert "data" in data

        # Output should be more compact (no indentation)
        assert "\n" not in output or output.count("\n") < 10


class TestMarkdownRenderer:
    """Test the MarkdownRenderer class."""

    def test_render_processing_result(self, sample_processing_result):
        """Test rendering a ProcessingResult as Markdown."""
        renderer = MarkdownRenderer()
        output = renderer.render(sample_processing_result)

        # Check Markdown structure
        assert output.startswith("# Document Summary:")
        assert "## Summary" in output
        assert "## File Information" in output
        assert "## Processing Metadata" in output
        assert output.endswith("*")  # Footer with timestamp

        # Check content
        assert "test_document.txt" in output
        assert "This is a test document" in output
        assert "**Path:**" in output
        assert "**Size:**" in output

    def test_render_error_result(self, error_processing_result):
        """Test rendering an error result as Markdown."""
        renderer = MarkdownRenderer()
        output = renderer.render(error_processing_result)

        assert "## ⚠️ Error" in output
        assert "**Code:** `E001`" in output
        assert "**Message:** Failed to process document" in output
        assert "```json" in output  # Details should be in JSON block

    def test_render_result_list(
        self, sample_processing_result, error_processing_result
    ):
        """Test rendering a list of results as Markdown."""
        renderer = MarkdownRenderer()
        results = [sample_processing_result, error_processing_result]
        output = renderer.render(results)

        assert output.startswith("# Processing Results (2 files)")
        assert "## Result 1" in output
        assert "## Result 2" in output

    def test_render_dict(self):
        """Test rendering a generic dictionary as Markdown."""
        renderer = MarkdownRenderer()
        data = {"status": "success", "items": ["a", "b", "c"]}
        output = renderer.render(data)

        assert output.startswith("# Results")
        assert "## Status" in output
        assert "## Items" in output
        assert "```json" in output  # Lists should be in JSON blocks


class TestPlainTextRenderer:
    """Test the PlainTextRenderer class."""

    def test_render_processing_result(self, sample_processing_result):
        """Test rendering a ProcessingResult as plain text."""
        renderer = PlainTextRenderer()
        output = renderer.render(sample_processing_result)

        # Check structure
        assert output.startswith("Document Summary:")
        assert "SUMMARY:" in output
        assert "FILE INFO:" in output
        assert "METADATA:" in output
        assert "Generated:" in output

        # Check content
        assert "test_document.txt" in output
        assert "This is a test document" in output
        assert "Path: test_document.txt" in output
        assert "Size: 0.00 MB" in output

    def test_render_error_result(self, error_processing_result):
        """Test rendering an error result as plain text."""
        renderer = PlainTextRenderer()
        output = renderer.render(error_processing_result)

        assert "ERROR:" in output
        assert "Code: E001" in output
        assert "Message: Failed to process document" in output
        assert "Details:" in output

    def test_render_result_list(
        self, sample_processing_result, error_processing_result
    ):
        """Test rendering a list of results as plain text."""
        renderer = PlainTextRenderer()
        results = [sample_processing_result, error_processing_result]
        output = renderer.render(results)

        assert output.startswith("Processing Results (2 files)")
        assert "--- Result 1 ---" in output
        assert "--- Result 2 ---" in output

    def test_render_dict(self):
        """Test rendering a generic dictionary as plain text."""
        renderer = PlainTextRenderer()
        data = {"status": "success", "count": 42}
        output = renderer.render(data)

        assert output.startswith("Results")
        assert "Status:" in output
        assert "success" in output
        assert "Count:" in output
        assert "42" in output


class TestRendererIntegration:
    """Integration tests for all renderers."""

    def test_all_renderers_handle_same_data(self, sample_processing_result):
        """Test that all renderers can handle the same data without errors."""
        renderers = [
            RichRenderer(),
            JsonRenderer(),
            MarkdownRenderer(),
            PlainTextRenderer(),
        ]

        for renderer in renderers:
            output = renderer.render(sample_processing_result)
            assert isinstance(output, str)
            assert len(output) > 0
            assert "test_document.txt" in output

    def test_all_renderers_handle_empty_data(self):
        """Test that all renderers gracefully handle empty/minimal data."""
        minimal_result = ProcessingResult(
            file=FileSelection(path="empty.txt"),
            summary=None,
            metadata=None,
            error=None,
        )

        renderers = [
            RichRenderer(),
            JsonRenderer(),
            MarkdownRenderer(),
            PlainTextRenderer(),
        ]

        for renderer in renderers:
            output = renderer.render(minimal_result)
            assert isinstance(output, str)
            assert len(output) > 0
            assert "empty.txt" in output
