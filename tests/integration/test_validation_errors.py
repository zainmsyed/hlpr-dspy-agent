import pytest

try:
    from hlpr.config.validators import ConfigValidator
except Exception:  # noqa: BLE001
    ConfigValidator = None


def test_validation_errors_reported():
    if ConfigValidator is None:
        pytest.fail("ConfigValidator not implemented yet")
    validator = ConfigValidator(None)
    bad = {"provider": "invalid", "format": "zzz", "chunk_size": -1}
    result = validator.validate_config(bad)
    assert result.is_valid is False
    assert len(result.errors) >= 1
