import pytest

try:
    from hlpr.config.platform import PlatformDefaults
except Exception:  # noqa: BLE001
    PlatformDefaults = None


def test_platform_defaults_immutable():
    if PlatformDefaults is None:
        pytest.fail("PlatformDefaults not implemented yet")
    defaults = PlatformDefaults()
    assert hasattr(defaults, "default_provider")
    assert "local" in defaults.supported_providers
    with pytest.raises(AttributeError):
        defaults.default_provider = "changed"
