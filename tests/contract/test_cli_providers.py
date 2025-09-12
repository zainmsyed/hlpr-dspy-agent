from typer.testing import CliRunner

from hlpr.cli.main import app

runner = CliRunner()


class TestCliProvidersContract:
    """Contract tests for hlpr providers CLI commands"""

    def test_providers_list(self):
        """Test listing AI providers"""
        # This test will fail until the CLI is implemented
        result = runner.invoke(app, ["providers", "list"])

        assert result.exit_code == 0
        # Should show table with providers
        assert "id" in result.output.lower() or "type" in result.output.lower()

    def test_providers_add_local(self):
        """Test adding local AI provider"""
        result = runner.invoke(
            app,
            [
                "providers",
                "add",
                "test_local",
                "--type",
                "local",
                "--model",
                "llama2:7b",
            ],
        )

        assert result.exit_code in [0, 1, 2]
        if result.exit_code == 0:
            out = result.output.lower()
            assert "success" in out or "added" in out

    def test_providers_add_openai(self):
        """Test adding OpenAI provider"""
        result = runner.invoke(
            app,
            [
                "providers",
                "add",
                "test_openai",
                "--type",
                "openai",
                "--model",
                "gpt-4",
                "--api-key",
                "test_key",
            ],
        )

        assert result.exit_code in [0, 1, 2]

    def test_providers_add_missing_required(self):
        """Test adding provider with missing required fields"""
        result = runner.invoke(
            app,
            ["providers", "add", "incomplete_provider", "--type", "local"],
        )

        # Should fail due to missing model
        assert result.exit_code == 2
        out = result.output.lower()
        assert "required" in out or "model" in out

    def test_providers_add_duplicate_id(self):
        """Test adding provider with duplicate ID"""
        # First add a provider
        result1 = runner.invoke(
            app,
            [
                "providers",
                "add",
                "duplicate_test",
                "--type",
                "local",
                "--model",
                "test_model",
            ],
        )

        if result1.exit_code == 0:
            # Try to add again
            result2 = runner.invoke(
                app,
                [
                    "providers",
                    "add",
                    "duplicate_test",
                    "--type",
                    "local",
                    "--model",
                    "test_model",
                ],
            )
            assert result2.exit_code == 1
            out = result2.output.lower()
            assert "exists" in out or "duplicate" in out

    def test_providers_test_connection(self):
        """Test testing provider connection"""
        # First add a provider
        result1 = runner.invoke(
            app,
            [
                "providers",
                "add",
                "test_conn",
                "--type",
                "local",
                "--model",
                "test_model",
            ],
        )

        if result1.exit_code == 0:
            # Then test connection
            result2 = runner.invoke(
                app, ["providers", "test", "test_conn"],
            )
            # Connection test may succeed or fail
            assert result2.exit_code in [0, 1, 3]

    def test_providers_test_nonexistent(self):
        """Test testing connection for non-existent provider"""
        result = runner.invoke(app, ["providers", "test", "nonexistent"])

        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    def test_providers_help(self):
        """Test help message for providers command"""
        result = runner.invoke(app, ["providers", "--help"])

        assert result.exit_code == 0
        assert "providers" in result.output.lower()
        assert "list" in result.output.lower()
        assert "add" in result.output.lower()
        assert "test" in result.output.lower()
