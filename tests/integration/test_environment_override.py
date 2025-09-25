import pytest

try:
    from hlpr.config.loader import ConfigLoader
except Exception:  # noqa: BLE001
    ConfigLoader = None


def test_env_overrides_defaults(monkeypatch):
    if ConfigLoader is None:
        pytest.fail("ConfigLoader not implemented yet")
    monkeypatch.setenv("HLPR_DEFAULT_PROVIDER", "openai")
    loader = ConfigLoader(None, None)
    result = loader.load_config()
    assert result.config.provider == "openai"
    monkeypatch.delenv("HLPR_DEFAULT_PROVIDER", raising=False)
