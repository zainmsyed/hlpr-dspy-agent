
from hlpr.config import HlprConfig


def test_config_defaults(monkeypatch):
    # Ensure no HLPR_* env vars -> defaults returned
    monkeypatch.delenv("HLPR_MAX_FILE_SIZE", raising=False)
    monkeypatch.delenv("HLPR_MAX_TEXT_LENGTH", raising=False)
    monkeypatch.delenv("HLPR_MAX_MEMORY_FILE_SIZE", raising=False)
    monkeypatch.delenv("HLPR_DEFAULT_TIMEOUT", raising=False)
    monkeypatch.delenv("HLPR_DEFAULT_FAST_FAIL_SECONDS", raising=False)
    monkeypatch.delenv("HLPR_ALLOWED_ORIGINS", raising=False)

    cfg = HlprConfig.from_env()

    assert cfg.max_file_size == HlprConfig.max_file_size
    assert cfg.max_text_length == HlprConfig.max_text_length
    assert cfg.max_memory_file_size == HlprConfig.max_memory_file_size
    assert cfg.default_timeout == HlprConfig.default_timeout


def test_config_env_overrides(monkeypatch):
    monkeypatch.setenv("HLPR_MAX_FILE_SIZE", "1234")
    monkeypatch.setenv("HLPR_DEFAULT_TIMEOUT", "60")
    monkeypatch.setenv(
        "HLPR_ALLOWED_ORIGINS", "http://localhost:3000, https://example.com",
    )

    cfg = HlprConfig.from_env()

    assert cfg.max_file_size == 1234
    assert cfg.default_timeout == 60
    assert cfg.allowed_origins == ["http://localhost:3000", "https://example.com"]


def test_config_invalid_values(monkeypatch):
    # Non-integer values should fall back to defaults
    monkeypatch.setenv("HLPR_MAX_FILE_SIZE", "not_an_int")
    monkeypatch.setenv("HLPR_DEFAULT_TIMEOUT", "-5")

    cfg = HlprConfig.from_env()

    # invalid int -> default
    assert cfg.max_file_size == HlprConfig.max_file_size
    # negative timeout -> fallback to default
    assert cfg.default_timeout == HlprConfig.default_timeout
