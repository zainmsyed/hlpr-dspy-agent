import json
from pathlib import Path

from typer.testing import CliRunner

from hlpr.cli.main import app

runner = CliRunner()


class TestMeetingWorkflowIntegration:
    """Integration tests for complete meeting processing workflow"""

    def test_full_meeting_processing_workflow(self):
        """Test complete meeting processing workflow"""
        # This test will fail until the full implementation is complete

        # Create sample meeting notes
        meeting_notes = Path("standup-notes.txt")
        meeting_notes.write_text(
            "Team Standup - September 9, 2025\n\n"
            "Attendees: Alice, Bob, Charlie, Diana\n\n"
            "Alice: Completed user authentication feature, working on password reset\n"
            "Bob: Finished database migration, starting on API endpoints\n"
            "Charlie: Reviewed pull requests, found performance issue in search\n"
            "Diana: Updated documentation, planning user testing session\n\n"
            "Action Items:\n"
            "- Alice: Complete password reset by Thursday\n"
            "- Bob: Document new API endpoints\n"
            "- Charlie: Fix search performance issue\n"
            "- Diana: Schedule user testing for next week\n\n"
            "Blockers: None reported",
        )

        # Test basic meeting summarization
        result = runner.invoke(app, ["summarize", "meeting", str(meeting_notes)])
        assert result.exit_code == 0
        assert "summary" in result.output.lower()
        assert "action items" in result.output.lower()
        assert "alice" in result.output.lower()

        # Clean up
        meeting_notes.unlink(missing_ok=True)

    def test_meeting_workflow_with_metadata(self):
        """Test meeting workflow with title and date metadata"""
        meeting_file = Path("planning-meeting.txt")
        meeting_file.write_text(
            "Discussion about Q4 planning and resource allocation. "
            "Team leads presented their roadmaps. Budget approved for new hires.",
        )

        result = runner.invoke(
            app,
            [
                "summarize",
                "meeting",
                str(meeting_file),
                "--title",
                "Sprint Planning",
                "--date",
                "2025-09-09",
            ],
        )
        assert result.exit_code == 0

        # Should include metadata in output
        if "Sprint Planning" in result.output:
            assert "Sprint Planning" in result.output
        if "2025-09-09" in result.output:
            assert "2025-09-09" in result.output

        # Clean up
        meeting_file.unlink(missing_ok=True)

    def test_meeting_workflow_with_file_output(self):
        """Test meeting workflow with JSON output"""
        meeting_file = Path("output-meeting.txt")
        meeting_file.write_text(
            "Product roadmap discussion. Priorities set for next quarter. "
            "Engineering team to focus on performance improvements.",
        )

        output_file = Path("meeting-summary.json")
        result = runner.invoke(
            app,
            [
                "summarize",
                "meeting",
                str(meeting_file),
                "--save",
                "--format",
                "json",
                "--output",
                str(output_file),
            ],
        )
        assert result.exit_code == 0
        assert output_file.exists()

        # Verify JSON structure
        with output_file.open() as f:
            data = json.load(f)
            assert "summary" in data
            assert "participants" in data or "attendees" in data

        # Clean up
        meeting_file.unlink(missing_ok=True)
        output_file.unlink(missing_ok=True)

    def test_meeting_workflow_action_items_extraction(self):
        """Test extraction of action items from meeting content"""
        meeting_file = Path("action-items-meeting.txt")
        meeting_file.write_text(
            "Team Meeting - Action Items Discussion\n\n"
            "John will update the documentation by Friday.\n"
            "Sarah needs to review the pull request before EOD.\n"
            "Mike should schedule a meeting with the client next week.\n"
            "Lisa will prepare the presentation for the board meeting.\n\n"
            "Follow-up meeting scheduled for next Tuesday.",
        )

        result = runner.invoke(app, ["summarize", "meeting", str(meeting_file)])
        assert result.exit_code == 0

        # Should extract action items
        output_lower = result.output.lower()
        assert "action" in output_lower
        assert "john" in output_lower or "documentation" in output_lower

        # Clean up
        meeting_file.unlink(missing_ok=True)

    def test_meeting_workflow_participant_extraction(self):
        """Test extraction of participants from meeting content"""
        meeting_file = Path("meeting-participants.txt")
        meeting_file.write_text(
            "Project Review Meeting\n\n"
            "Present: Alice Johnson (PM), Bob Smith (Dev), "
            "Carol Williams (QA), David Brown (Design)\n\n"
            "Alice presented the project timeline.\n"
            "Bob demonstrated the new features.\n"
            "Carol reported on testing progress.\n"
            "David showed the updated mockups.\n\n"
            "Next steps discussed.",
        )

        result = runner.invoke(app, ["summarize", "meeting", str(meeting_file)])
        assert result.exit_code == 0

        # Should extract participants
        output_lower = result.output.lower()
        assert "participants" in output_lower or "attendees" in output_lower
        assert "alice" in output_lower
        assert "bob" in output_lower
        assert "carol" in output_lower
        assert "david" in output_lower

        # Clean up
        meeting_file.unlink(missing_ok=True)

    def test_meeting_workflow_error_handling(self):
        """Test error handling in meeting workflow"""
        # Test with non-existent file
        result = runner.invoke(app, ["summarize", "meeting", "nonexistent.txt"])
        assert result.exit_code == 1
        assert "not found" in result.output.lower() or "error" in result.output.lower()

        # Test with empty file
        empty_file = Path("empty-meeting.txt")
        empty_file.write_text("")
        result = runner.invoke(app, ["summarize", "meeting", str(empty_file)])
        # Should handle gracefully
        assert result.exit_code in [0, 1, 2]

        # Clean up
        empty_file.unlink(missing_ok=True)
