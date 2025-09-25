# Future Features: Modular Platform Roadmap

Date: 2025-09-25
Source: Rescoping of Feature 004 (Guided Workflow)
Status: Draft reference (to be split into individual feature specs under `specs/005-*` etc.)

## Overview
Several tasks initially bundled into the guided workflow feature (004) are platform-wide infrastructure concerns. To maintain modularity and align with the constitution (modular, testable, incremental), these have been extracted into an epic (T070) and grouped into four new features.

## Feature Matrix
| Feature | Focus | Key Tasks (original IDs) | Primary Modules | Risks |
|---------|-------|---------------------------|-----------------|-------|
| 005 Core Configuration & UI | Centralized config + UI strings + recovery | T044, T046, T052, T060 | `hlpr.config`, `hlpr.cli` | Drift between constants & runtime defaults |
| 006 CLI Infrastructure & Validation | UX polish, validation, help, naming | T040, T041, T042, T043, T048, T057 | `hlpr.cli.*`, `hlpr.exceptions` | Backward compatibility of commands |
| 007 Document Processing Pipeline | Streaming, batch orchestration, progress, taxonomy | T053, T054, T055, T056, T058 | `hlpr.document.*`, `hlpr.cli.batch` | Performance regressions; concurrency edge cases |
| 008 Persistence & Secure Storage | Preferences & secure template storage | T049, T050, T051, T059 | `hlpr.models.*`, `hlpr.io` | Data migration & permissions portability |

## Dependencies
- Feature 007 depends on stable configuration defaults from Feature 005.
- Feature 006 (naming standardization) should land before broad documentation rewrites.
- Feature 008 builds on storage directory conventions possibly formalized in Feature 005.

## Detailed Breakdown
### Feature 005: Core Configuration & UI
Goals:
- Single source for provider/format defaults & limits.
- UI string externalization for testability and future localization.
- Config reset safety and schema validation.
Deliverables:
- `src/hlpr/config/platform.py` (new) exporting constants + loaders.
- Validation routine invoked at startup; fallback to defaults on corruption.
- Tests: corruption recovery, default override precedence, UI string referential integrity.

### Feature 006: CLI Infrastructure & Validation
Goals:
- Consistent error surfaces and retry flows.
- In-app contextual help triggered via `--help-context` or interactive hint key.
- Path & input sanitization with explicit taxonomy.
Deliverables:
- `validators.py` enhancements (sanitization + structured errors).
- `help_display.py` context sections (providers, formats, performance tips).
- Naming normalization script or doc check.
- Tests: invalid paths, retry logic, provider/format help rendering.

### Feature 007: Document Processing Pipeline
Goals:
- Memory-efficient parsing for large files (streaming: PDFs page-wise, text chunked).
- Batch orchestrator with per-file + aggregate progress using Rich.
- Unified progress instrumentation accessible from all CLI entrypoints.
- Expanded error taxonomy (ParsingTimeoutError, ChunkingError, ProviderBackoffError).
Deliverables:
- `document/streaming.py` (chunk & page iterators with heuristics).
- `cli/batch.py` or enhancement of existing batch processor for uniform interface.
- Progress adapter: multi-task progress with quiet fallback.
- Tests: large simulated file, mixed success/failure batch, streaming vs non-streaming parity.

### Feature 008: Persistence & Secure Storage
Goals:
- Preferences system (last used provider, format, chunk size) with opt-in persistence.
- Harden saved command/template storage (0600 perms, atomic writes already present).
- Optional interactive file picker re-introduction with pluggable backend.
Deliverables:
- `models/user_preferences.py` finalization (already partially present?).
- Permission enforcement helper + audit test.
- Tests: permission downgrade detection, preference round-trip, template load after permission fix.

## Cross-Cutting Acceptance Criteria
- All new modules have at least 85% line coverage (unit + integration).
- No regressions on existing guided workflow tests.
- Lint + type checks pass (ruff + mypy if enabled later).
- Performance: batch summary of 5 small docs < 3s local provider baseline.

## Proposed Sequencing (Incremental PRs)
1. 005-A: Extract constants (providers, formats, chunk sizes) to `config/platform.py` + tests.
2. 007-A: Introduce streaming parser (guarded by flag; off by default) + tests.
3. 007-B: Unified progress adapter refactoring (reuse RichDisplay.operation_progress) + tests.
4. 007-C: Batch orchestrator revision + integration test.
5. 005-B: Config reset & recovery + corruption tests.
6. 006-A: Validation & enhanced error messages.
7. 008-A: Preferences persistence minimal implementation.
8. 006-B: In-app help & naming standardization.
9. 008-B: Secure storage permission hardening.
10. 007-D: Error taxonomy expansion.
11. 006-C / 008-C: File picker (optional) + docs & troubleshooting.

## Risks & Mitigations
| Risk | Mitigation |
|------|-----------|
| Streaming introduces subtle parsing differences | Add golden small-file comparison tests |
| Concurrency + local model blocking | Provide concurrency cap & doc guidance |
| Permission handling breaks on Windows | Conditional chmod logic with platform guard |
| Naming standardization breaks scripts | Provide alias commands & deprecation warnings |

## Tooling & Scripts
- Add `scripts/dev/coverage.sh` for quick coverage diffs.
- Optional pre-commit hook: enforce naming and import boundaries.

## Open Questions
- Do we need a plugin mechanism for additional providers? (Defer)
- Should preferences be scoped per working directory? (Potential future enhancement)

## Next Actions
1. Create specs directories: `specs/005-core-config/`, `specs/006-cli-infra/`, etc. (future step)
2. Implement 005-A PR after guided mode core stabilizes.
3. Track epic progress via T070 updates in `tasks.md`.

---
Prepared as a living reference for modular feature extraction.
