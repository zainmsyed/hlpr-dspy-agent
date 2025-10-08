from pathlib import Path

from hlpr.config.manager import ConfigurationManager
from hlpr.config.models import ConfigurationPaths


def make_paths(tmp_path: Path) -> ConfigurationPaths:
    d = tmp_path / "hlpr_test_ops"
    return ConfigurationPaths(
        config_dir=d,
        config_file=d / "config.yaml",
        env_file=d / ".env",
        backup_dir=d / "backups",
    )


def test_atomic_write_and_backup(tmp_path: Path):
    paths = make_paths(tmp_path)
    mgr = ConfigurationManager(paths=paths)

    # Save a config and ensure files created
    state = mgr.load_configuration()
    mgr.save_configuration(state)
    assert paths.config_file.exists()
    assert paths.env_file.exists()

    # Corrupt the config and ensure backup on load
    paths.config_file.write_text(":::corrupt:::\n")

    # load_configuration should detect the unreadable YAML, move the
    # corrupted file to backups and return defaults
    mgr.load_configuration()

    # When corrupted, backup dir should contain at least one file with the
    # 'config.yaml.corrupted' prefix
    backups = list(paths.backup_dir.glob("config.yaml.corrupted.*"))
    assert len(backups) >= 1
    # The backup content should contain our corruption marker
    content = backups[0].read_text()
    assert ":::corrupt:::" in content


def test_large_config_size_triggers_backup(tmp_path: Path):
    paths = make_paths(tmp_path)
    mgr = ConfigurationManager(paths=paths)

    # Ensure config exists
    state = mgr.load_configuration()
    mgr.save_configuration(state)
    assert paths.config_file.exists()

    # Write a large file (>1MB)
    large_content = "A" * (1 * 1024 * 1024 + 10)
    paths.config_file.write_text(large_content)

    # load_configuration should detect oversize and back it up with .oversize
    new_state = mgr.load_configuration()
    assert isinstance(new_state, type(state))

    backups = list(paths.backup_dir.glob("config.yaml.corrupted.*.oversize"))
    assert len(backups) >= 1
    # backup content should contain the large marker (first few bytes)
    assert backups[0].read_text()[:10] == "A" * 10
