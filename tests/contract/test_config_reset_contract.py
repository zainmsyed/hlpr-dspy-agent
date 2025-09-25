import pytest

try:
    from hlpr.config.loader import ConfigLoader
except Exception:  # noqa: BLE001
    ConfigLoader = None


def test_config_reset_contract_interface():
    if ConfigLoader is None:
        pytest.fail("ConfigLoader not implemented yet")
    loader = ConfigLoader(None, None)
    if hasattr(loader, "reset_config"):
        success = loader.reset_config(preserve_user_data=True)
        assert isinstance(success, bool)
    else:
        pytest.fail("reset_config API missing")
