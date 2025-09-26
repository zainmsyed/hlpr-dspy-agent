Migration notes — hlpr configuration changes
===========================================

Date: 2025-09-26

This project introduced a centralized configuration defaults and a schema migration
system to preserve backward compatibility for existing configuration files.

Key points
----------
- Centralized defaults are exposed as `PLATFORM_DEFAULTS` from the `hlpr.config`
  package. This contains default provider, format, and chunk sizes used by the
  CLI and loader.
- Environment-aware helpers `get_env_provider(default)` and
  `get_env_format(default)` are provided by `hlpr.config` to ensure environment
  variables take precedence in a stable, testable way. Supported env vars:
  - `HLPR_PROVIDER` / `HLPR_DEFAULT_PROVIDER`
  - `HLPR_FORMAT` / `HLPR_DEFAULT_FORMAT`
- A migration registry lives at `src/hlpr/config/migration.py`. Call `migrate_config`
  (re-exported from `hlpr.config`) to transform legacy config dictionaries into
  the latest schema before loading.

What changed
------------
- CLI modules now use `hlpr.config.PLATFORM_DEFAULTS` and the env helpers. This
  centralizes default values and reduces duplication across the codebase.
- `ConfigLoader.load_config()` applies `migrate_config()` to file-based configs
  before merging with environment and default values.

How to migrate existing configs
-------------------------------
If you have existing configuration files that use legacy keys (for example
`default_provider` or `default_chunk_size`), the migration system will rename
those keys into the new schema during load. No manual edits are required in most
cases — however you can run the migration helper directly in Python for bulk
operations:

```py
from hlpr.config import migrate_config

with open('path/to/config.json') as fh:
    cfg = json.load(fh)

new = migrate_config(cfg)
print(new)
```

Notes and troubleshooting
-------------------------
- If the loader returns unexpected defaults, check your environment variables
  (`HLPR_PROVIDER` / `HLPR_DEFAULT_PROVIDER`, `HLPR_FORMAT` / `HLPR_DEFAULT_FORMAT`).
- If you need to enforce a timeout for local model providers in CI, pass an
  explicit `timeout` to the summarizer or set the runtime configuration.

Contact
-------
If you want a PR prepared with these changes or prefer the migration to be a
separate CLI command (bulk migration), open an issue or request it in the PR
description.
# Configuration Migration Notes

This project includes a small, versioned configuration migration system to
safely upgrade older user configuration files to the current schema.

Key points
- User config files (default: `~/.hlpr/config.json`) are automatically
  migrated on load by `ConfigLoader.load_config()` via `migrate_config(...)`.
- The migration registry lives in `src/hlpr/config/migration.py` and supports
  sequential schema upgrades. The current schema version is exported by that
  module.
- A conservative policy is used: if migration fails, the loader falls back to
  using the raw file contents (and does not crash). Use `ConfigRecovery` or
  manual inspection if recovery is required.

Common legacy-to-current mappings
- `default_provider` &rarr; `provider`
- `default_chunk_size` &rarr; `chunk_size`

How to add migrations
1. Register a migration function using the provided decorator in
   `src/hlpr/config/migration.py`.
2. New migrations must be idempotent and only operate on the config dict.
3. Add unit tests under `tests/unit` verifying migration behavior.

Troubleshooting
- If you suspect a config file is causing issues, move it temporarily and
  re-run the CLI to let defaults take effect. Example:

```bash
mv ~/.hlpr/config.json ~/.hlpr/config.json.bak
hlpr summarize document documents/examples/welcome_to_wrtr.md
```

Contact
- For any migration issues, open an issue in the repo and include the
  problematic config.json (sanitized) and the `migrate_config` output.
