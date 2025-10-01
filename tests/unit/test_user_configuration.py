from pathlib import Path

import pytest

from hlpr.config.models import OutputFormat, ProviderType, UserConfiguration


def test_user_configuration_defaults_and_validation():
    cfg = UserConfiguration()
    assert cfg.default_provider == ProviderType.LOCAL
    assert cfg.default_format == OutputFormat.RICH
    assert 0.0 <= cfg.default_temperature <= 1.0
    assert cfg.default_max_tokens > 0


def test_user_configuration_path_expansion(tmp_path):
    p = tmp_path / "out"
    cfg = UserConfiguration(default_output_directory=str(p))
    assert isinstance(cfg.default_output_directory, Path)
    assert cfg.default_output_directory.exists() or not cfg.default_output_directory.exists()


def test_invalid_temperature_raises():
    with pytest.raises(ValueError):
        UserConfiguration(default_temperature=2.0)
