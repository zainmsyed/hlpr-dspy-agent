import pytest

try:
    from hlpr.config.loader import ConfigLoader
except Exception:  # noqa: BLE001
    ConfigLoader = None

import json
from pathlib import Path


def test_user_config_file_applied(tmp_path, monkeypatch):
    if ConfigLoader is None:
        pytest.fail("ConfigLoader not implemented yet")
    monkeypatch.setenv("HOME", str(tmp_path))
    cfg_dir = Path(tmp_path) / ".hlpr"
    cfg_dir.mkdir()
    cfg_file = cfg_dir / "config.json"
    cfg_file.write_text(json.dumps({"provider": "anthropic", "format": "md", "chunk_size": 4096}))
    loader = ConfigLoader(None, None)
    result = loader.load_config()
    assert result.config.provider == "anthropic"
