
from hlpr.config.models import (
    APICredentials,
    ConfigurationPaths,
    ConfigurationState,
    UserConfiguration,
)


def test_load_defaults_when_no_files(tmp_path):
    paths = ConfigurationPaths(
        config_dir=tmp_path,
        config_file=tmp_path / "config.yaml",
        env_file=tmp_path / ".env",
        backup_dir=tmp_path / "backups",
    )

    from hlpr.config.manager import ConfigurationManager

    mgr = ConfigurationManager(paths=paths)
    state = mgr.load_configuration()
    assert isinstance(state, ConfigurationState)
    assert state.config.default_provider == UserConfiguration().default_provider


def test_save_and_load_roundtrip(tmp_path):
    paths = ConfigurationPaths.default()
    # Use tmp dir for test
    paths = ConfigurationPaths(
        config_dir=tmp_path,
        config_file=tmp_path / "config.yaml",
        env_file=tmp_path / ".env",
        backup_dir=tmp_path / "backups",
    )

    from hlpr.config.manager import ConfigurationManager

    mgr = ConfigurationManager(paths=paths)
    state = ConfigurationState(
        config=UserConfiguration(default_temperature=0.5, default_max_tokens=1000),
        credentials=APICredentials(openai_api_key="sk-test-123"),
    )

    mgr.save_configuration(state)

    # Ensure files exist
    assert paths.config_file.exists()
    assert paths.env_file.exists()

    loaded = mgr.load_configuration()
    assert loaded.config.default_temperature == 0.5
    assert loaded.credentials.openai_api_key == "sk-test-123"
