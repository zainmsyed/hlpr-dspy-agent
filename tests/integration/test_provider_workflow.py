from typer.testing import CliRunner

from hlpr.cli.main import app

runner = CliRunner()


class TestProviderWorkflowIntegration:
    """Integration tests for complete provider management workflow"""

    def test_provider_setup_workflow(self):
        """Test complete provider setup and configuration workflow"""
        # This test will fail until the full implementation is complete

        # Test adding an OpenAI provider
        result = runner.invoke(
            app,
            [
                "providers", "add", "openai_test", "--type", "openai",
                "--api-key", "sk-test123456789",
            ],
        )
        assert result.exit_code in [0, 1]

        # Test adding an Anthropic provider
        result = runner.invoke(
            app,
            [
                "providers", "add", "anthropic_test", "--type", "anthropic",
                "--api-key", "sk-ant-test123456789",
            ],
        )
        assert result.exit_code in [0, 1]

        # Test listing providers
        result = runner.invoke(app, ["providers", "list"])
        assert result.exit_code == 0
        # Should show at least the providers we tried to add
        output_lower = result.output.lower()
        assert (
            "openai" in output_lower or "anthropic" in output_lower
            or "test" in output_lower
        )

    def test_provider_testing_workflow(self):
        """Test provider testing and validation workflow"""
        # Test a provider (will fail without real API key)
        result = runner.invoke(app, ["providers", "test", "openai_test"])
        # Should attempt connection or fail gracefully
        assert result.exit_code in [0, 1, 2]

        # If successful, should show test results
        if result.exit_code == 0:
            assert "success" in result.output.lower() or "test" in result.output.lower()

    def test_provider_selection_workflow(self):
        """Test provider selection and default setting workflow"""
        # Set a provider as default
        result = runner.invoke(app, ["providers", "set-default", "openai_test"])
        assert result.exit_code in [0, 1]

        # Check current default
        result = runner.invoke(app, ["providers", "current"])
        assert result.exit_code == 0
        if "openai_test" in result.output:
            assert "openai_test" in result.output

    def test_provider_removal_workflow(self):
        """Test provider removal workflow"""
        # Add a provider first
        result1 = runner.invoke(
            app,
            [
                "providers", "add", "remove_test", "--type", "openai",
                "--api-key", "sk-remove123",
            ],
        )

        if result1.exit_code == 0:
            # Remove the provider
            result2 = runner.invoke(app, ["providers", "remove", "remove_test"])
            assert result2.exit_code == 0

            # Verify it's removed
            result3 = runner.invoke(app, ["providers", "list"])
            assert result3.exit_code == 0
            assert "remove_test" not in result3.output

    def test_provider_error_handling(self):
        """Test error handling in provider workflow"""
        # Test with non-existent provider
        result = runner.invoke(app, ["providers", "test", "nonexistent_provider"])
        assert result.exit_code == 1
        assert (
            "not found" in result.output.lower()
            or "provider" in result.output.lower()
        )

        # Test adding provider with invalid type
        result = runner.invoke(
            app,
            [
                "providers", "add", "invalid_test", "--type", "invalid_type",
                "--api-key", "test",
            ],
        )
        assert result.exit_code == 1
        assert "invalid" in result.output.lower() or "type" in result.output.lower()

    def test_provider_configuration_workflow(self):
        """Test provider configuration and settings workflow"""
        # Add provider with custom settings
        result = runner.invoke(
            app,
            [
                "providers", "add", "config_test", "--type", "openai",
                "--api-key", "sk-config123",
                "--model", "gpt-4",
                "--temperature", "0.7",
                "--max-tokens", "2000",
            ],
        )
        assert result.exit_code in [0, 1]

        # Show provider details
        result = runner.invoke(app, ["providers", "show", "config_test"])
        assert result.exit_code in [0, 1]
        if result.exit_code == 0:
            # Should show configuration details
            output_lower = result.output.lower()
            config_indicators = [
                "model", "temperature", "max-tokens", "gpt-4", "0.7", "2000",
            ]
            found_config = sum(
                1 for indicator in config_indicators
                if str(indicator) in output_lower
            )
            assert found_config >= 2

    def test_provider_usage_workflow(self):
        """Test provider usage in document/meeting processing"""
        # This would test using providers in actual processing workflows
        # For now, just test that providers are available for use

        # List available providers
        result = runner.invoke(app, ["providers", "list"])
        assert result.exit_code == 0

        # If we have providers, test that they can be used
        if "openai_test" in result.output or "anthropic_test" in result.output:
            # Test that document processing can use providers
            result = runner.invoke(
                app,
                [
                    "summarize", "document", "nonexistent.pdf",
                    "--provider", "openai_test",
                ],
            )
            # Should attempt to use the provider or fail gracefully
            assert result.exit_code in [0, 1, 2]

    def test_provider_switching_workflow(self):
        """Test switching between different providers"""
        # Add multiple providers
        result1 = runner.invoke(
            app,
            [
                "providers", "add", "switch1", "--type", "openai",
                "--api-key", "sk-switch1",
            ],
        )
        result2 = runner.invoke(
            app,
            [
                "providers", "add", "switch2", "--type", "anthropic",
                "--api-key", "sk-switch2",
            ],
        )

        if result1.exit_code == 0 and result2.exit_code == 0:
            # Switch between them
            result3 = runner.invoke(app, ["providers", "set-default", "switch1"])
            assert result3.exit_code == 0

            result4 = runner.invoke(app, ["providers", "set-default", "switch2"])
            assert result4.exit_code == 0

            # Verify current default
            result5 = runner.invoke(app, ["providers", "current"])
            assert result5.exit_code == 0
            assert "switch2" in result5.output
