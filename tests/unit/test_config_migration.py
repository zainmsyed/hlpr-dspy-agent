from hlpr.config.migration import migrate, MigrationError, CURRENT_SCHEMA_VERSION


def test_migrate_legacy_keys():
    legacy = {"default_provider": "openai", "default_chunk_size": 4096}
    migrated = migrate(legacy)
    assert migrated["schema_version"] == CURRENT_SCHEMA_VERSION
    assert migrated["provider"] == "openai"
    assert migrated["chunk_size"] == 4096


def test_migrate_future_version_raises():
    cfg = {"schema_version": CURRENT_SCHEMA_VERSION + 1}
    try:
        migrate(cfg)
        raised = False
    except MigrationError:
        raised = True
    assert raised
