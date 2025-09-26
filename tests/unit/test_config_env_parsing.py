import os
from pathlib import Path

import pytest

from hlpr.config.loader import ConfigLoader


def test_hlpr_config_path_env_resolved(monkeypatch, tmp_path):
    env_path = tmp_path / "myconfig.json"
    monkeypatch.setenv("HLPR_CONFIG_PATH", str(env_path))

    loader = ConfigLoader()
    # Should use the env-provided path (absolute/resolved)
    assert Path(str(loader.config_path)).absolute() == env_path.absolute()


def test_nested_env_keys_and_json_values(monkeypatch):
    monkeypatch.delenv("HLPR_CONFIG_PATH", raising=False)
    monkeypatch.setenv("HLPR_LOG__LEVEL", "info")
    monkeypatch.setenv("HLPR_FLAG", "true")
    monkeypatch.setenv("HLPR_JSON_LIST", "[\"a\", \"b\"]")
    monkeypatch.setenv("HLPR_CHUNK_SIZE", "2048")

    loader = ConfigLoader()
    env_conf = loader._load_from_env()

    # Nested key created from double-underscore
    assert isinstance(env_conf.get("log"), dict)
    assert env_conf["log"]["level"] == "info"

    # Boolean parsed
    assert env_conf.get("flag") is True

    # JSON array parsed
    assert env_conf.get("json_list") == ["a", "b"]

    # Numeric parsed
    assert env_conf.get("chunk_size") == 2048
