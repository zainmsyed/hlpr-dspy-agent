import pytest

try:
    from hlpr.config.loader import ConfigLoader
except Exception:  # allow tests to exist even if module is not fully implemented  # noqa: BLE001
    ConfigLoader = None


def test_config_loader_contract_returns_loadresult():
    """Contract: ConfigLoader.load_config should return a LoadResult-like object with config and load_time_ms."""
    if ConfigLoader is None:
        pytest.fail("ConfigLoader not implemented yet")
    loader = ConfigLoader(None, None)
    result = loader.load_config()
    assert hasattr(result, "config")
    assert hasattr(result, "load_time_ms")
    assert isinstance(result.load_time_ms, (float, int))
