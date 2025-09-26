def test_config_package_exports():
    import hlpr.config as cfg

    # Ensure package re-exports exist and are usable
    assert hasattr(cfg, "PLATFORM_DEFAULTS")
    assert hasattr(cfg, "get_env_provider")
    assert hasattr(cfg, "get_env_format")
    assert hasattr(cfg, "migrate_config")

    # Basic sanity checks
    assert cfg.get_env_provider("local") in (None, "local", "openai", "anthropic", "groq", "together")
    assert isinstance(cfg.PLATFORM_DEFAULTS.default_chunk_size, int)
