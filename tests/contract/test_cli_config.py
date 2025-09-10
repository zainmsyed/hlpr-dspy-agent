from typer.testing import CliRunner

from hlpr.cli.main import app

runner = CliRunner()


class TestCliConfigContract:
    """Contract tests for hlpr config CLI commands"""

    def test_config_show_default(self):
        """Test showing default configuration"""
        # This test will fail until the CLI is implemented
        result = runner.invoke(app, ["config", "show"])

        assert result.exit_code == 0
        # Should show configuration in yaml format by default
        assert "default_llm" in result.output or "providers" in result.output

    def test_config_show_json_format(self):
        """Test showing configuration in JSON format"""
        result = runner.invoke(app, ["config", "show", "--format", "json"])

        assert result.exit_code == 0
        # Should be valid JSON
        import json
        try:
            config = json.loads(result.output)
            assert isinstance(config, dict)
        except json.JSONDecodeError:
            assert False, "Output is not valid JSON"

    def test_config_show_hide_sensitive(self):
        """Test hiding sensitive configuration values"""
        result = runner.invoke(app, ["config", "show", "--hide-sensitive"])

        assert result.exit_code == 0
        # Should not contain sensitive values like API keys
        assert "api_key" not in result.output.lower() or "***" in result.output

    def test_config_set_value(self):
        """Test setting a configuration value"""
        result = runner.invoke(app, ["config", "set", "test_key", "test_value"])

        assert result.exit_code == 0
        assert "set" in result.output.lower() or "updated" in result.output.lower()

    def test_config_set_invalid_key(self):
        """Test setting invalid configuration key"""
        result = runner.invoke(app, ["config", "set", "invalid.key.with.dots", "value"])

        # Should succeed or validate key format
        assert result.exit_code in [0, 1]

    def test_config_get_existing_key(self):
        """Test getting an existing configuration value"""
        # First set a value
        set_result = runner.invoke(app, ["config", "set", "test_get_key", "test_get_value"])
        if set_result.exit_code == 0:
            # Then get it
            get_result = runner.invoke(app, ["config", "get", "test_get_key"])
            assert get_result.exit_code == 0
            assert "test_get_value" in get_result.output

    def test_config_get_nonexistent_key(self):
        """Test getting a non-existent configuration key"""
        result = runner.invoke(app, ["config", "get", "nonexistent_key"])

        assert result.exit_code == 1
        assert "not found" in result.output.lower() or "not set" in result.output.lower()

    def test_config_get_without_key(self):
        """Test config get command without key argument"""
        result = runner.invoke(app, ["config", "get"])

        assert result.exit_code == 2  # Missing argument
        assert "key" in result.output.lower()

    def test_config_set_without_value(self):
        """Test config set command without value argument"""
        result = runner.invoke(app, ["config", "set", "test_key"])

        assert result.exit_code == 2  # Missing argument
        assert "value" in result.output.lower()

    def test_config_help(self):
        """Test help message for config command"""
        result = runner.invoke(app, ["config", "--help"])

        assert result.exit_code == 0
        assert "config" in result.output.lower()
        assert "show" in result.output.lower()
        assert "set" in result.output.lower()
        assert "get" in result.output.lower()
