from hlpr.config.manager import ConfigurationManager
from hlpr.config.models import ConfigurationPaths


def _make_paths(tmp_path):
    return ConfigurationPaths(
        config_dir=tmp_path,
        config_file=tmp_path / "config.yaml",
        env_file=tmp_path / ".env",
        backup_dir=tmp_path / "backups",
    )


def test_env_parsing_basic(tmp_path):
    paths = _make_paths(tmp_path)
    paths.env_file.write_text("OPENAI_API_KEY=sk-test-123\n")
    mgr = ConfigurationManager(paths=paths)
    creds = mgr._parse_env_file()
    assert creds.openai_api_key == "sk-test-123"


def test_env_parsing_quoted_and_spaced(tmp_path):
    paths = _make_paths(tmp_path)
    paths.env_file.write_text(
        "OPENAI_API_KEY = \"sk-quoted\"\nGOOGLE_API_KEY=  sk-spaces  \nANTHROPIC_API_KEY='sk-single'\n"
    )
    mgr = ConfigurationManager(paths=paths)
    creds = mgr._parse_env_file()
    assert creds.openai_api_key == "sk-quoted"
    assert creds.google_api_key == "sk-spaces"
    assert creds.anthropic_api_key == "sk-single"


def test_env_parsing_malformed_lines(tmp_path):
    paths = _make_paths(tmp_path)
    paths.env_file.write_text(
        "INVALID_LINE_NO_EQUALS\n=VALUE_NO_KEY\nOPENAI_API_KEY=ok\n"
    )
    mgr = ConfigurationManager(paths=paths)
    creds = mgr._parse_env_file()
    assert creds.openai_api_key == "ok"


def test_env_parsing_empty_values(tmp_path):
    paths = _make_paths(tmp_path)
    paths.env_file.write_text("OPENAI_API_KEY=\nGOOGLE_API_KEY=    \n")
    mgr = ConfigurationManager(paths=paths)
    creds = mgr._parse_env_file()
    assert creds.openai_api_key is None
    assert creds.google_api_key is None
