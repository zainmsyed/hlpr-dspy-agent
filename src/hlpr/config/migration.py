"""Configuration schema migration helpers.

Provides a minimal migration registry and a `migrate` function that applies
sequential migrations to bring older configuration dicts to the current
schema version. This is intentionally small and testable; more migrations
can be registered as needed.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

CURRENT_SCHEMA_VERSION = 1


class MigrationError(RuntimeError):
    pass


# Each migration is a function that accepts and returns a dict
Migration = Callable[[dict[str, Any]], dict[str, Any]]


_MIGRATIONS: dict[int, Migration] = {}


def register_migration(version: int):
    def _decorator(fn: Migration) -> Migration:
        _MIGRATIONS[version] = fn
        return fn

    return _decorator


def migrate(config: dict[str, Any]) -> dict[str, Any]:
    """Migrate a configuration dict to the current schema version.

        Contract:
        - Reads optional top-level key `schema_version`; if absent, assumes 0.
        - Applies sequential registered migrations up to CURRENT_SCHEMA_VERSION.
        - Returns a new dict; does not mutate the input in place.

        Raises:
        - MigrationError: if the config is from a newer schema version or if a
            required migration step is missing.
        """
    version = int(config.get("schema_version", 0))
    if version > CURRENT_SCHEMA_VERSION:
        raise MigrationError(
            f"Config schema version {version} is newer than supported "
            f"{CURRENT_SCHEMA_VERSION}"
        )

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
def _migrate_0_to_1(cfg: dict[str, Any]) -> dict[str, Any]:
    out = dict(cfg)
    # rename legacy 'default_provider' -> 'provider'
    if "default_provider" in out and "provider" not in out:
        out["provider"] = out.pop("default_provider")
    # Ensure chunk size key name consistency
    if "default_chunk_size" in out and "chunk_size" not in out:
        out["chunk_size"] = out.pop("default_chunk_size")
    return out

