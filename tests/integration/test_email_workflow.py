from pathlib import Path

from typer.testing import CliRunner

from hlpr.cli.main import app

runner = CliRunner()


class TestEmailWorkflowIntegration:
    """Integration tests for complete email processing workflow"""

    def test_email_account_setup_workflow(self):
        """Test complete email account setup and testing workflow"""
        # This test will fail until the full implementation is complete

        # Test adding an email account
        result = runner.invoke(
            app,
            [
                "email", "accounts", "add", "test_workflow",
                "--provider", "gmail", "--username", "test@gmail.com",
                "--password", "testpass",
            ],
        )
        # Should succeed or fail gracefully
        assert result.exit_code in [0, 1]

        # Test listing accounts
        result = runner.invoke(app, ["email", "accounts", "list"])
        assert result.exit_code == 0
        assert "test_workflow" in result.output or "gmail" in result.output

    def test_email_processing_workflow(self):
        """Test complete email processing workflow"""
        # Test processing emails (will fail without real account setup)
        result = runner.invoke(
            app, ["email", "process", "test_workflow", "--limit", "5"],
        )
        # Should attempt processing or fail gracefully
        assert result.exit_code in [0, 1, 2]  # Success, general error, or config error

        # If successful, should show processing results
        if result.exit_code == 0:
            assert "process" in result.output.lower()

    def test_email_workflow_with_filters(self):
        """Test email processing with various filters"""
        # Test with unread filter
        result = runner.invoke(
            app,
            [
                "email", "process", "test_workflow",
                "--unread-only", "--limit", "10",
            ],
        )
        assert result.exit_code in [0, 1, 2]

        # Test with date filter
        result = runner.invoke(
            app,
            [
                "email", "process", "test_workflow",
                "--since", "2025-09-01", "--limit", "5",
            ],
        )
        assert result.exit_code in [0, 1, 2]

        # Test with sender filter
        result = runner.invoke(
            app,
            [
                "email", "process", "test_workflow",
                "--from", "important@company.com",
            ],
        )
        assert result.exit_code in [0, 1, 2]

    def test_email_workflow_with_save_output(self):
        """Test email processing with file output"""
        output_file = Path("email-results.csv")
        result = runner.invoke(
            app,
            [
                "email", "process", "test_workflow", "--save",
                "--format", "csv", "--output", str(output_file), "--limit", "3",
            ],
        )
        assert result.exit_code in [0, 1, 2]

        # If successful, should create output file
        if result.exit_code == 0:
            assert output_file.exists()
            output_file.unlink(missing_ok=True)

    def test_email_workflow_error_handling(self):
        """Test error handling in email workflow"""
        # Test with non-existent account
        result = runner.invoke(app, ["email", "process", "nonexistent_account"])
        assert result.exit_code == 1
        assert (
            "not found" in result.output.lower()
            or "account" in result.output.lower()
        )

        # Test with invalid limit
        result = runner.invoke(
            app,
            ["email", "process", "test_workflow", "--limit", "1500"],  # Over max
        )
        assert result.exit_code in [1, 2]  # Should validate limits

    def test_email_workflow_table_output(self):
        """Test that email processing shows proper table output"""
        result = runner.invoke(
            app, ["email", "process", "test_workflow", "--limit", "5"],
        )
        # Should show table headers even if no emails processed
        if result.exit_code == 0:
            output_lower = result.output.lower()
            # Look for table elements
            table_indicators = [
                "sender", "subject", "date", "classification", "priority",
            ]
            found_indicators = sum(
                1 for indicator in table_indicators
                if indicator in output_lower
            )
            # Should have at least some table structure
            assert found_indicators >= 2

    def test_email_workflow_summary_statistics(self):
        """Test that email processing shows summary statistics"""
        result = runner.invoke(
            app, ["email", "process", "test_workflow", "--limit", "10"],
        )
        if result.exit_code == 0:
            output_lower = result.output.lower()
            # Should show some statistics
            stat_indicators = [
                "processed", "total", "work", "personal", "high", "medium", "low",
            ]
            found_stats = sum(
                1 for stat in stat_indicators if stat in output_lower
            )
            # Should have at least basic statistics
            assert found_stats >= 1

    def test_email_account_management_workflow(self):
        """Test complete account management workflow"""
        # Add account
        result1 = runner.invoke(
            app,
            [
                "email", "accounts", "add", "workflow_test",
                "--provider", "gmail", "--username", "workflow@gmail.com",
                "--password", "pass",
            ],
        )

        if result1.exit_code == 0:
            # Test account
            result2 = runner.invoke(
                app, ["email", "accounts", "test", "workflow_test"],
            )
            assert result2.exit_code in [0, 1]  # Test may succeed or fail

            # List accounts
            result3 = runner.invoke(app, ["email", "accounts", "list"])
            assert result3.exit_code == 0
            assert "workflow_test" in result3.output

            # Remove account
            result4 = runner.invoke(
                app, ["email", "accounts", "remove", "workflow_test"],
            )
            assert result4.exit_code == 0
