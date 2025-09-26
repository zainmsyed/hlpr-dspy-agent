# Tasks: Core Configuration and UI Management System

**Input**: Design documents from `/specs/005-core-configuration-and-ui-management/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Tech stack: Python 3.11+, Pydantic, pytest
   → Project type: Single project (extends hlpr CLI)
   → Structure: src/hlpr/config/, tests/contract/, tests/integration/, tests/unit/
2. Load design documents:
   → data-model.md: 6 entities (PlatformDefaults, PlatformConfig, UIStringManager, ConfigValidator, ConfigRecovery, ConfigLoader)
   → contracts/: 8 API contracts for configuration operations
   → quickstart.md: 8 validation scenarios
3. Generate tasks by category:
   → Setup: Dependencies, project structure, linting
   → Tests: 8 contract tests, 8 integration tests  
   → Core: 6 model/service implementations
   → Integration: File I/O, cross-platform permissions, migration
   → Polish: Performance validation, documentation
4. Applied task rules:
   → Different files marked [P] for parallel execution
   → Tests before implementation (TDD approach)
   → Dependencies enforced through sequencing
5. SUCCESS: 37 tasks generated, dependency-ordered
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/hlpr/config/`, `tests/contract/`, `tests/integration/`, `tests/unit/`
- All paths assume hlpr repository root

## Phase 3.1: Setup
- [x] T001 Create configuration module structure in src/hlpr/config/
- [x] T002 Install Pydantic dependency via uv add pydantic
- [x] T003 [P] Configure pytest for configuration testing in pytest.ini

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (API Behavior)
- [x] T004 [P] Contract test ConfigLoader.load_config() in tests/contract/test_config_loader_contract.py
- [x] T005 [P] Contract test ConfigValidator.validate_config() in tests/contract/test_config_validator_contract.py  
- [x] T006 [P] Contract test ConfigRecovery.recover_config() in tests/contract/test_config_recovery_contract.py
- [x] T007 [P] Contract test UIStringManager.get() in tests/contract/test_ui_strings_contract.py
- [x] T008 [P] Contract test PlatformDefaults access in tests/contract/test_platform_defaults_contract.py
- [x] T009 [P] Contract test environment override precedence in tests/contract/test_environment_override_contract.py
- [x] T010 [P] Contract test configuration reset in tests/contract/test_config_reset_contract.py
- [x] T011 [P] Contract test performance constraints in tests/contract/test_performance_contract.py

### Integration Tests (End-to-End Scenarios)  
- [x] T012 [P] Integration test fresh installation loading in tests/integration/test_fresh_installation.py
- [x] T013 [P] Integration test environment variable override in tests/integration/test_environment_override.py
- [x] T014 [P] Integration test configuration file creation in tests/integration/test_config_file_creation.py
- [x] T015 [P] Integration test validation errors in tests/integration/test_validation_errors.py
- [x] T016 [P] Integration test corruption recovery in tests/integration/test_corruption_recovery.py
- [x] T017 [P] Integration test UI strings validation in tests/integration/test_ui_strings_validation.py
- [x] T018 [P] Integration test configuration reset in tests/integration/test_config_reset.py
- [x] T019 [P] Integration test cross-platform permissions in tests/integration/test_cross_platform_permissions.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Platform Constants and Configuration Models
- [x] T020 [P] PlatformDefaults immutable constants in src/hlpr/config/platform.py
- [x] T021 [P] PlatformConfig Pydantic model with validation in src/hlpr/config/platform.py
- [x] T022 [P] UIStringKeys and UIStringManager in src/hlpr/config/ui_strings.py (extend existing)

### Validation and Error Handling
- [x] T023 [P] ValidationResult and ValidationError models in src/hlpr/config/validators.py
- [x] T024 ConfigValidator implementation with actionable errors in src/hlpr/config/validators.py

### Recovery System
- [x] T025 [P] RecoveryAction enum and RecoveryResult model in src/hlpr/config/recovery.py
- [x] T026 ConfigRecovery corruption detection and atomic recovery in src/hlpr/config/recovery.py

### Configuration Loading
- [x] T027 [P] ConfigSource enum and LoadResult model in src/hlpr/config/loader.py  
- [x] T028 ConfigLoader precedence handling and file operations in src/hlpr/config/loader.py

## Phase 3.4: Integration

### File System Integration
- [x] T029 Cross-platform permission handling in ConfigRecovery
- [x] T030 Atomic configuration file operations in ConfigRecovery
- [x] T031 Environment variable processing in ConfigLoader

Integration tests: T012-T019 were executed; all passed with one test skipped (platform/optional). See test logs for skipped-test details.

### Backward Compatibility
- [x] T032 Extend existing config.py with platform constants integration and new option compatibility
- [x] T033 Update CLI modules to use centralized constants (guided mode, batch processing)
 - Implementation notes: CLI Typer options across `src/hlpr/cli/` were updated to
   call `hlpr.config.get_env_provider(...)` and `hlpr.config.get_env_format(...)`,
   and to use `hlpr.config.PLATFORM_DEFAULTS` instead of in-line literal defaults
   (for example, replacing hard-coded "local" and "rich").
 - Tests: Unit and integration tests were executed; the full test suite passed
   locally (pytest run on 2025-09-26). `ConfigLoader.load_config()` now applies
   `migrate_config()` to file-based configs before merging to ensure legacy keys
   are transformed.
- [x] T034 Migration helpers for existing configuration files with safe new option defaults
- [x] T037 Configuration schema migration system in src/hlpr/config/migration.py

## Phase 3.5: Polish

### Performance and Validation
- [x] T035 [P] Unit tests for edge cases in tests/unit/test_config_edge_cases.py
- [x] T036 [P] Performance benchmarks (<100ms loading, <10ms validation) in tests/unit/test_config_performance.py

## Dependencies
- Setup (T001-T003) before all other phases
- Contract tests (T004-T011) before implementation (T020-T028)
- Integration tests (T012-T019) before implementation (T020-T028)  
- T020-T021 (platform models) before T024, T026, T028 (services that use them)
- T022 (UI strings) before T024 (validator that uses UI strings)
- T023 (validation models) before T024 (validator implementation)
- T025 (recovery models) before T026 (recovery implementation)
- T027 (loader models) before T028 (loader implementation)
- Core implementation (T020-T028) before integration (T029-T037)
- Integration (T029-T037) before polish (T035-T036)
- T037 (schema migration) depends on T024 (validator) and T026 (recovery)

## Parallel Execution Examples

### Contract Tests (Phase 3.2a)
```bash
# Launch T004-T011 together (all different files):
Task: "Contract test ConfigLoader.load_config() in tests/contract/test_config_loader_contract.py"
Task: "Contract test ConfigValidator.validate_config() in tests/contract/test_config_validator_contract.py"  
Task: "Contract test ConfigRecovery.recover_config() in tests/contract/test_config_recovery_contract.py"
Task: "Contract test UIStringManager.get() in tests/contract/test_ui_strings_contract.py"
```

### Integration Tests (Phase 3.2b)
```bash
# Launch T012-T019 together (all different files):
Task: "Integration test fresh installation loading in tests/integration/test_fresh_installation.py"
Task: "Integration test environment variable override in tests/integration/test_environment_override.py"
Task: "Integration test configuration file creation in tests/integration/test_config_file_creation.py"
Task: "Integration test validation errors in tests/integration/test_validation_errors.py"
```

### Model Creation (Phase 3.3a)
```bash
# Launch T020-T022 together (different files):
Task: "PlatformDefaults immutable constants in src/hlpr/config/platform.py"
Task: "UIStringKeys and UIStringManager in src/hlpr/config/ui_strings.py (extend existing)"
# Note: T021 waits for T020 (same file)
```

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**: 8 contracts → 8 contract test tasks [P]
2. **From Data Model**: 6 entities → 6 model/service tasks (some [P], some sequential)
3. **From Quickstart**: 8 scenarios → 8 integration test tasks [P]
4. **From Plan**: Dependencies, performance, backward compatibility → setup and integration tasks

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All 8 contracts have corresponding tests (T004-T011)
- [x] All 6 entities have model/implementation tasks (T020-T028)
- [x] All 8 quickstart scenarios have integration tests (T012-T019)
- [x] All tests come before implementation (Phase 3.2 before 3.3)
- [x] Parallel tasks are truly independent (different files)
- [x] Each task specifies exact file path
- [x] No [P] task modifies same file as another [P] task
- [x] Dependencies properly enforced through sequencing
- [x] Performance requirements covered (T036)
- [x] Backward compatibility addressed (T032-T034, T037)
- [x] Schema version migration covered (T037)

## Notes
- [P] tasks target different files and have no dependencies
- Verify ALL tests fail before implementing (TDD compliance)
- Commit after each completed task
- Follow existing hlpr code patterns and import structure
- Maintain backward compatibility with existing config.py
- Performance targets: <100ms config loading, <10ms validation
- Cross-platform compatibility required (Linux, macOS, Windows)