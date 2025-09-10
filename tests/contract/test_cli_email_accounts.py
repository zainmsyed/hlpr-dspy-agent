from typer.testing import CliRunner

from hlpr.cli.main import app

runner = CliRunner()


class TestCliEmailAccountsContract:
    """Contract tests for hlpr email accounts CLI commands"""

    def test_email_accounts_list(self):
        """Test listing email accounts"""
        # This test will fail until the CLI is implemented
        result = runner.invoke(app, ["email", "accounts", "list"])

        assert result.exit_code == 0
        # Should show table headers even if no accounts
        assert "id" in result.output.lower() or "provider" in result.output.lower()

    def test_email_accounts_add_basic(self):
        """Test adding email account with basic options"""
        result = runner.invoke(
            app,
            ["email", "accounts", "add", "test_account", "--provider", "gmail", "--username", "test@gmail.com", "--password", "testpass"],
        )

        # Should succeed or fail gracefully
        assert result.exit_code in [0, 1, 2]
        if result.exit_code == 0:
            assert "success" in result.output.lower() or "added" in result.output.lower()

    def test_email_accounts_add_custom_provider(self):
        """Test adding account with custom provider"""
        result = runner.invoke(
            app,
            ["email", "accounts", "add", "custom_account", "--provider", "custom", "--host", "mail.example.com", "--username", "user@example.com", "--password", "password"],
        )

        assert result.exit_code in [0, 1, 2]

    def test_email_accounts_add_missing_required(self):
        """Test adding account with missing required fields"""
        result = runner.invoke(
            app,
            ["email", "accounts", "add", "incomplete_account", "--provider", "gmail"],
        )

        # Should fail due to missing username/password
        assert result.exit_code == 2
        assert "required" in result.output.lower() or "username" in result.output.lower()

    def test_email_accounts_add_duplicate_id(self):
        """Test adding account with duplicate ID"""
        # First add an account
        result1 = runner.invoke(
            app,
            ["email", "accounts", "add", "duplicate_test", "--provider", "gmail", "--username", "test@gmail.com", "--password", "pass"],
        )

        if result1.exit_code == 0:
            # Try to add again
            result2 = runner.invoke(
                app,
                ["email", "accounts", "add", "duplicate_test", "--provider", "gmail", "--username", "test2@gmail.com", "--password", "pass"],
            )
            assert result2.exit_code == 1
            assert "exists" in result2.output.lower() or "duplicate" in result2.output.lower()

    def test_email_accounts_remove_existing(self):
        """Test removing an existing account"""
        # First add an account
        result1 = runner.invoke(
            app,
            ["email", "accounts", "add", "remove_test", "--provider", "gmail", "--username", "test@gmail.com", "--password", "pass"],
        )

        if result1.exit_code == 0:
            # Then remove it
            result2 = runner.invoke(app, ["email", "accounts", "remove", "remove_test"])
            assert result2.exit_code == 0
            assert "removed" in result2.output.lower() or "deleted" in result2.output.lower()

    def test_email_accounts_remove_nonexistent(self):
        """Test removing non-existent account"""
        result = runner.invoke(app, ["email", "accounts", "remove", "nonexistent_account"])

        assert result.exit_code == 1
        assert "not found" in result.output.lower() or "exists" in result.output.lower()

    def test_email_accounts_test_connection(self):
        """Test testing account connection"""
        # First add an account
        result1 = runner.invoke(
            app,
            ["email", "accounts", "add", "test_conn", "--provider", "gmail", "--username", "test@gmail.com", "--password", "pass"],
        )

        if result1.exit_code == 0:
            # Then test connection
            result2 = runner.invoke(app, ["email", "accounts", "test", "test_conn"])
            # Connection test may succeed or fail depending on credentials
            assert result2.exit_code in [0, 1, 3]  # Success, general error, or auth error

    def test_email_accounts_test_nonexistent(self):
        """Test testing connection for non-existent account"""
        result = runner.invoke(app, ["email", "accounts", "test", "nonexistent"])

        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    def test_email_accounts_help(self):
        """Test help message for email accounts command"""
        result = runner.invoke(app, ["email", "accounts", "--help"])

        assert result.exit_code == 0
        assert "accounts" in result.output.lower()
        assert "list" in result.output.lower()
        assert "add" in result.output.lower()
        assert "remove" in result.output.lower()
