"""Configuration schema migration helpers.

Provides a minimal migration registry and a `migrate` function that applies
sequential migrations to bring older configuration dicts to the current
schema version. This is intentionally small and testable; more migrations
can be registered as needed.
"""
from __future__ import annotations

from typing import Callable, Dict, Any

CURRENT_SCHEMA_VERSION = 1


class MigrationError(RuntimeError):
    pass


# Each migration is a function that accepts and returns a dict
Migration = Callable[[Dict[str, Any]], Dict[str, Any]]


_MIGRATIONS: dict[int, Migration] = {}


def register_migration(version: int):
    def _decorator(fn: Migration) -> Migration:
        _MIGRATIONS[version] = fn
        return fn

    return _decorator


def migrate(config: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate `config` in-place (returns a new dict) to CURRENT_SCHEMA_VERSION.

    Expects optional top-level key "schema_version". If absent, assumes 0.
    """
    version = int(config.get("schema_version", 0))
    if version > CURRENT_SCHEMA_VERSION:
        raise MigrationError(f"Config schema version {version} is newer than supported {CURRENT_SCHEMA_VERSION}")

    data = dict(config)
    while version < CURRENT_SCHEMA_VERSION:
        next_version = version + 1
        migration = _MIGRATIONS.get(next_version)
        if not migration:
            raise MigrationError(f"No migration registered for version {next_version}")
        data = migration(data)
        data["schema_version"] = next_version
        version = next_version

    return data


# Example migration: bring old 'default_provider' top-level key to 'provider'
@register_migration(1)
def _migrate_0_to_1(cfg: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(cfg)
    # rename legacy 'default_provider' -> 'provider'
    if "default_provider" in out and "provider" not in out:
        out["provider"] = out.pop("default_provider")
    # Ensure chunk size key name consistency
    if "default_chunk_size" in out and "chunk_size" not in out:
        out["chunk_size"] = out.pop("default_chunk_size")
    return out

