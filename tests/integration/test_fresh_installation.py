import pytest

try:
    from hlpr.config.loader import ConfigLoader
except Exception:  # noqa: BLE001
    ConfigLoader = None


def test_fresh_installation_loads_defaults(tmp_path, monkeypatch):
    if ConfigLoader is None:
        pytest.fail("ConfigLoader not implemented yet")
    monkeypatch.setenv("HOME", str(tmp_path))
    loader = ConfigLoader(None, None)
    result = loader.load_config()
    assert result.config is not None
    assert result.config.provider == "local"
