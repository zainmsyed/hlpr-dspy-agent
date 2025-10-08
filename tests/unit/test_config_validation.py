from pathlib import Path

import yaml

from hlpr.config.manager import ConfigurationManager
from hlpr.config.models import ConfigurationPaths, ProviderType


def make_paths(tmp_path: Path) -> ConfigurationPaths:
    d = tmp_path / "hlpr_test"
    return ConfigurationPaths(
        config_dir=d,
        config_file=d / "config.yaml",
        env_file=d / ".env",
        backup_dir=d / "backups",
    )


def test_validate_valid_and_invalid_config(tmp_path: Path):
    paths = make_paths(tmp_path)
    mgr = ConfigurationManager(paths=paths)

    # Default state should validate
    state = mgr.load_configuration()
    res = mgr.validate_configuration(state)
    assert res.is_valid is True

    # Write an invalid config.yaml (bad provider). The manager treats invalid
    # model data as corrupted: it will back up the file and return defaults.
    paths.config_dir.mkdir(parents=True, exist_ok=True)
    bad_data = yaml.safe_dump({"provider": "not-a-provider"})
    mgr._atomic_write(mgr.paths.config_file, bad_data)

    state = mgr.load_configuration()

    # The manager should have returned defaults and not the invalid provider.
    assert isinstance(state.config.default_provider, ProviderType)
