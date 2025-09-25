import pytest

try:
    from hlpr.config.validators import ConfigValidator
except Exception:  # noqa: BLE001
    ConfigValidator = None


def test_validator_valid_config_structure():
    if ConfigValidator is None:
        pytest.fail("ConfigValidator not implemented yet")
    validator = ConfigValidator(None)
    valid_config = {"provider": "local", "format": "rich", "chunk_size": 8192}
    result = validator.validate_config(valid_config)
    assert hasattr(result, "is_valid")
    assert result.is_valid is True
