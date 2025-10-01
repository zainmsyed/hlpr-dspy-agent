import os

from hlpr.config import defaults, validators, migration, templates


def test_defaults_values():
    # ensure some expected defaults exist and are of correct types
    assert isinstance(defaults.DEFAULT_PROVIDER, str)
    assert isinstance(defaults.DEFAULT_TEMPERATURE, float)
    assert defaults.DEFAULT_MAX_TOKENS > 0


def test_validator_temperature():
    assert validators.validate_temperature(0.5)
    assert not validators.validate_temperature(-0.1)
    assert not validators.validate_temperature(2.0)


def test_validator_max_tokens():
    assert validators.validate_max_tokens(1024)
    assert not validators.validate_max_tokens(0)


def test_api_key_format():
    assert validators.is_valid_api_key_format("sk-abc123")
    assert not validators.is_valid_api_key_format("not-a-key")


def test_migration_noop():
    data = {"some": "value"}
    out = migration.migrate_config_v1_to_v2(data)
    assert out is data or out == data


def test_templates_generate():
    d = {"provider": defaults.DEFAULT_PROVIDER, "temperature": defaults.DEFAULT_TEMPERATURE}
    y = templates.default_config_yaml(d)
    assert "# hlpr configuration file" in y
    e = templates.default_env_template()
    assert "OPENAI_API_KEY" in e
