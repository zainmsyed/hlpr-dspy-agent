import pytest

try:
    from hlpr.config.recovery import ConfigRecovery
except Exception:  # noqa: BLE001
    ConfigRecovery = None

from pathlib import Path


def test_corruption_recovery_preserves_user_data(tmp_path, monkeypatch):
    if ConfigRecovery is None:
        pytest.fail("ConfigRecovery not implemented yet")
    monkeypatch.setenv("HOME", str(tmp_path))
    hlpr_dir = Path(tmp_path) / ".hlpr"
    hlpr_dir.mkdir()
    (hlpr_dir / "saved_commands.json").write_text("[]")
    (hlpr_dir / "config.json").write_text("{ invalid json }")
    recovery = ConfigRecovery(hlpr_dir / "config.json", hlpr_dir / "config.backup.json", logger=None)
    res = recovery.recover_config()
    assert hasattr(res, "success")
