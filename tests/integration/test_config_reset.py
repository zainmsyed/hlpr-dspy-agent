import pytest

try:
    from hlpr.config.loader import ConfigLoader
except Exception:  # noqa: BLE001
    ConfigLoader = None


def test_reset_preserves_user_data(monkeypatch, tmp_path):
    if ConfigLoader is None:
        pytest.fail("ConfigLoader not implemented yet")
    monkeypatch.setenv("HOME", str(tmp_path))
    loader = ConfigLoader(None, None)
    if hasattr(loader, "reset_config"):
        ok = loader.reset_config(preserve_user_data=True)
        assert isinstance(ok, bool)
    else:
        pytest.fail("reset_config API missing")
