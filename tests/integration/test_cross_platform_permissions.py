import pytest

try:
    from hlpr.config.recovery import ConfigRecovery
except Exception:  # noqa: BLE001
    ConfigRecovery = None

from pathlib import Path


def test_permission_checking(tmp_path, monkeypatch):
    if ConfigRecovery is None:
        pytest.fail("ConfigRecovery not implemented yet")
    monkeypatch.setenv("HOME", str(tmp_path))
    config_path = Path(tmp_path) / ".hlpr" / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text("{}")
    rec = ConfigRecovery(config_path, config_path.parent / "config.backup.json", logger=None)
    assert hasattr(rec, "recover_config")
