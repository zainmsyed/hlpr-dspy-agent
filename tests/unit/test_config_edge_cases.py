import json

import pytest

from hlpr.config.loader import ConfigLoader
from hlpr.config.ui_strings import UIStringManager
from hlpr.config.validators import ConfigValidator


def test_ui_string_manager_empty_raises():
    with pytest.raises(ValueError):
        UIStringManager({})


def test_validator_rejects_bad_provider_and_format():
    v = ConfigValidator()
    res = v.validate_config({"provider": "unsupported", "output_format": "weird"})
    assert not res.is_valid
    msgs = [e["msg"] for e in (res.errors or [])]
    assert any("unsupported provider" in m for m in msgs) or any("unsupported format" in m for m in msgs)


def test_loader_parses_env_overrides(tmp_path, monkeypatch):
    # Ensure environment overrides are respected and types coerced
    monkeypatch.setenv("HLPR_PROVIDER", "openai")
    monkeypatch.setenv("HLPR_OUTPUT_FORMAT", "json")
    monkeypatch.setenv("HLPR_CHUNK_SIZE", "4096")

    loader = ConfigLoader(config_path=tmp_path / "config.json")
    result = loader.load_config()
    assert result.config.provider == "openai"
    assert result.config.output_format == "json"
    assert result.config.chunk_size == 4096


def test_loader_handles_corrupt_file(tmp_path, monkeypatch):
    p = tmp_path / "config.json"
    p.write_text("not-a-json")
    loader = ConfigLoader(config_path=p)
    # Corrupt file should be treated as empty and not raise
    result = loader.load_config()
    assert result.config.provider in ("local",)


def test_reset_config_preserve_user_keys(tmp_path):
    p = tmp_path / "config.json"
    # Write a file with an extra key
    data = {"defaults": {"default_provider": "local"}, "extra": {"keep": 1}}
    p.write_text(json.dumps(data))
    loader = ConfigLoader(config_path=p)
    ok = loader.reset_config(preserve_user_data=True)
    assert ok
    loaded = json.loads(p.read_text())
    # extra key should still be present
    assert "extra" in loaded
