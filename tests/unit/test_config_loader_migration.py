import json
import tempfile
from pathlib import Path

from hlpr.config.loader import ConfigLoader


def test_loader_applies_migration(tmp_path):
    # Create a fake config file with legacy keys
    cfg = {"default_provider": "openai", "default_chunk_size": 4096}
    p = tmp_path / "config.json"
    p.write_text(json.dumps(cfg), encoding="utf-8")

    loader = ConfigLoader(config_path=p, defaults=None)
    result = loader.load_config()
    # Ensure legacy keys were migrated to the modern schema
    assert result.config.provider == "openai"
    assert result.config.chunk_size == 4096
