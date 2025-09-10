from pathlib import Path

from typer.testing import CliRunner

from hlpr.cli.main import app

runner = CliRunner()


class TestCliSummarizeDocumentContract:
    """Contract tests for hlpr summarize document CLI command"""

    def test_summarize_document_basic(self):
        """Test basic document summarization command"""
        # This test will fail until the CLI is implemented
        test_file = Path("test_document.txt")
        test_file.write_text("This is a test document for summarization.")

        result = runner.invoke(app, ["summarize", "document", str(test_file)])

        # Should succeed
        assert result.exit_code == 0
        assert "summary" in result.output.lower()
        assert "key points" in result.output.lower()

    def test_summarize_document_with_provider(self):
        """Test document summarization with specific provider"""
        test_file = Path("test_document.txt")
        test_file.write_text("Test content for provider-specific summarization.")

        result = runner.invoke(
            app, ["summarize", "document", "--provider", "local", str(test_file)],
        )

        assert result.exit_code == 0
        assert "summary" in result.output.lower()

    def test_summarize_document_save_output(self):
        """Test saving summary to file"""
        test_file = Path("test_document.txt")
        test_file.write_text("Content to be summarized and saved.")

        output_file = Path("summary.json")
        result = runner.invoke(
            app,
            ["summarize", "document", "--save", "--format", "json", "--output", str(output_file), str(test_file)],
        )

        assert result.exit_code == 0
        assert output_file.exists()
        # Clean up
        output_file.unlink(missing_ok=True)

    def test_summarize_document_file_not_found(self):
        """Test handling of non-existent file"""
        result = runner.invoke(app, ["summarize", "document", "nonexistent.txt"])

        assert result.exit_code == 1
        assert "not found" in result.output.lower() or "error" in result.output.lower()

    def test_summarize_document_unsupported_format(self):
        """Test handling of unsupported file format"""
        # Create a file with unsupported extension
        test_file = Path("test.unsupported")
        test_file.write_text("Unsupported format content.")

        result = runner.invoke(app, ["summarize", "document", str(test_file)])

        assert result.exit_code == 2
        assert "unsupported" in result.output.lower() or "format" in result.output.lower()

        # Clean up
        test_file.unlink(missing_ok=True)

    def test_summarize_document_help(self):
        """Test help message for summarize document command"""
        result = runner.invoke(app, ["summarize", "document", "--help"])

        assert result.exit_code == 0
        assert "summarize" in result.output.lower()
        assert "document" in result.output.lower()
        assert "provider" in result.output.lower()
