from pathlib import Path

from typer.testing import CliRunner

from hlpr.cli.main import app

runner = CliRunner()


class TestCliSummarizeMeetingContract:
    """Contract tests for hlpr summarize meeting CLI command"""

    def test_summarize_meeting_basic(self):
        """Test basic meeting summarization command"""
        # This test will fail until the CLI is implemented
        test_file = Path("meeting_notes.txt")
        test_file.write_text("Meeting notes: Discussed project timeline. Action items: John to update docs.")

        result = runner.invoke(app, ["summarize", "meeting", str(test_file)])

        assert result.exit_code == 0
        assert "overview" in result.output.lower()
        assert "key points" in result.output.lower()
        assert "action items" in result.output.lower()

    def test_summarize_meeting_with_title_and_date(self):
        """Test meeting summarization with custom title and date"""
        test_file = Path("meeting_notes.txt")
        test_file.write_text("Meeting content with custom metadata.")

        result = runner.invoke(
            app,
            ["summarize", "meeting", "--title", "Sprint Planning", "--date", "2025-09-09", str(test_file)],
        )

        assert result.exit_code == 0
        assert "sprint planning" in result.output.lower()

    def test_summarize_meeting_save_output(self):
        """Test saving meeting summary to file"""
        test_file = Path("meeting_notes.txt")
        test_file.write_text("Content to be summarized and saved as meeting notes.")

        output_file = Path("meeting_summary.json")
        result = runner.invoke(
            app,
            ["summarize", "meeting", "--save", "--format", "json", "--output", str(output_file), str(test_file)],
        )

        assert result.exit_code == 0
        assert output_file.exists()
        # Clean up
        output_file.unlink(missing_ok=True)

    def test_summarize_meeting_file_not_found(self):
        """Test handling of non-existent meeting file"""
        result = runner.invoke(app, ["summarize", "meeting", "nonexistent.txt"])

        assert result.exit_code == 1
        assert "not found" in result.output.lower() or "error" in result.output.lower()

    def test_summarize_meeting_unsupported_format(self):
        """Test handling of unsupported file format for meeting"""
        test_file = Path("meeting.pdf")
        test_file.write_text("Fake PDF content - should be rejected.")

        result = runner.invoke(app, ["summarize", "meeting", str(test_file)])

        assert result.exit_code == 2
        assert "unsupported" in result.output.lower() or "format" in result.output.lower()

        # Clean up
        test_file.unlink(missing_ok=True)

    def test_summarize_meeting_with_provider(self):
        """Test meeting summarization with specific AI provider"""
        test_file = Path("meeting_notes.txt")
        test_file.write_text("Meeting content for provider testing.")

        result = runner.invoke(
            app, ["summarize", "meeting", "--provider", "openai", str(test_file)],
        )

        assert result.exit_code == 0
        assert "meeting" in result.output.lower()

    def test_summarize_meeting_help(self):
        """Test help message for summarize meeting command"""
        result = runner.invoke(app, ["summarize", "meeting", "--help"])

        assert result.exit_code == 0
        assert "summarize" in result.output.lower()
        assert "meeting" in result.output.lower()
        assert "title" in result.output.lower()
        assert "date" in result.output.lower()
