# Tasks: Update Config Workflow

**Input**: Design documents from `/specs/007-update-config-workflow/`
**Prerequisites**: plan.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

## Execution Flow (main)
```
1. Load plan.md from feature directory
   ✓ Loaded: Python 3.11+, Typer, Rich, Pydantic, PyYAML (to be added)
   ✓ Structure: Single project - extends existing hlpr CLI application
2. Load optional design documents:
   ✓ data-model.md: UserConfiguration, APICredentials, ConfigurationState entities
   ✓ contracts/: ConfigurationManagerInterface, CLI commands (setup, show, edit, reset, validate)
   ✓ research.md: YAML+.env approach, file permissions, caching strategy
3. Generate tasks by category:
   ✓ Setup: PyYAML dependency, config module structure
   ✓ Tests: Contract tests for CLI commands, integration scenarios
   ✓ Core: Configuration models, manager implementation, CLI commands
   ✓ Integration: Existing command integration, migration utilities
   ✓ Polish: Unit tests, performance validation, error handling
4. Apply task rules:
   ✓ Different files = marked [P] for parallel execution
   ✓ Same file = sequential dependencies
   ✓ Tests before implementation (TDD approach)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   ✓ All contracts have tests
   ✓ All entities have models  
   ✓ All CLI commands implemented
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
Single project structure - paths from repository root:
- **Source**: `src/hlpr/config/`, `src/hlpr/cli/`
- **Tests**: `tests/contract/`, `tests/integration/`, `tests/unit/`

## Phase 3.1: Setup
- [ ] T001 Add PyYAML dependency to project: `uv add pyyaml`
- [ ] T002 Create configuration module structure in `src/hlpr/config/`
- [ ] T003 [P] Configure ruff linting rules for new config module

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests for CLI Commands
- [ ] T004 [P] Contract test `hlpr config setup` command in `tests/contract/test_config_setup.py`
- [ ] T005 [P] Contract test `hlpr config show` command in `tests/contract/test_config_show.py`
- [ ] T006 [P] Contract test `hlpr config edit` command in `tests/contract/test_config_edit.py`
- [ ] T007 [P] Contract test `hlpr config reset` command in `tests/contract/test_config_reset.py`
- [ ] T008 [P] Contract test `hlpr config validate` command in `tests/contract/test_config_validate.py`

### Integration Tests for User Scenarios
- [ ] T009 [P] Integration test first-time user setup scenario in `tests/integration/test_first_run_setup.py`
- [ ] T010 [P] Integration test returning user experience in `tests/integration/test_returning_user.py`
- [ ] T011 [P] Integration test configuration management workflow in `tests/integration/test_config_management.py`
- [ ] T012 [P] Integration test error recovery scenarios in `tests/integration/test_error_recovery.py`
- [ ] T013 [P] Integration test API key management in `tests/integration/test_api_key_management.py`
- [ ] T014 [P] Integration test configuration reset workflow in `tests/integration/test_config_reset_workflow.py`

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Configuration Data Models
- [ ] T015 [P] Implement ProviderType and OutputFormat enums in `src/hlpr/config/models.py`
- [ ] T016 [P] Implement UserConfiguration model with validation in `src/hlpr/config/models.py`
- [ ] T017 [P] Implement APICredentials model in `src/hlpr/config/models.py`
- [ ] T018 [P] Implement ConfigurationState model in `src/hlpr/config/models.py`
- [ ] T019 [P] Implement ConfigurationPaths utility class in `src/hlpr/config/models.py`
- [ ] T020 [P] Implement ValidationResult and error classes in `src/hlpr/config/models.py`

### Configuration Manager Implementation
- [ ] T021 Create ConfigurationManagerInterface in `src/hlpr/config/manager.py`
- [ ] T022 Implement file loading with YAML parsing in `src/hlpr/config/manager.py`
- [ ] T023 Implement file saving with atomic operations in `src/hlpr/config/manager.py`
- [ ] T024 Implement configuration validation logic in `src/hlpr/config/manager.py`
- [ ] T025 Implement graceful fallback for corrupted configs in `src/hlpr/config/manager.py`
- [ ] T026 Implement API key management (.env file handling) in `src/hlpr/config/manager.py`
- [ ] T027 Implement backup and restore functionality in `src/hlpr/config/manager.py`
- [ ] T028 Implement first-run detection in `src/hlpr/config/manager.py`

### CLI Commands Implementation
- [ ] T029 [P] Implement `hlpr config setup` command with Rich prompts in `src/hlpr/cli/config_commands.py`
- [ ] T030 [P] Implement `hlpr config show` command with formatting options in `src/hlpr/cli/config_commands.py`
- [ ] T031 [P] Implement `hlpr config edit` command with editor integration in `src/hlpr/cli/config_commands.py`
- [ ] T032 [P] Implement `hlpr config reset` command with confirmation in `src/hlpr/cli/config_commands.py`
- [ ] T033 [P] Implement `hlpr config validate` command with error reporting in `src/hlpr/cli/config_commands.py`

### Support Utilities
- [ ] T034 [P] Implement default configuration values in `src/hlpr/config/defaults.py`
- [ ] T035 [P] Implement configuration validation utilities in `src/hlpr/config/validators.py`
- [ ] T036 [P] Implement migration utilities for existing configs in `src/hlpr/config/migration.py`
- [ ] T037 [P] Create configuration file templates with placeholder examples in `src/hlpr/config/templates.py`

## Phase 3.4: Integration
- [ ] T038 Update main CLI entry point to load configuration at startup in `src/hlpr/cli/main.py`
- [ ] T039 Integrate config defaults into existing summarize commands in `src/hlpr/cli/`
- [ ] T040 Add configuration error handling to existing workflows
- [ ] T041 Implement environment variable override support
- [ ] T042 Update guided workflow to offer preference saving
- [ ] T043 Add API key validation for cloud providers in existing commands

## Phase 3.5: Polish

### Unit Tests
- [ ] T044 [P] Unit tests for UserConfiguration model validation in `tests/unit/test_user_configuration.py`
- [ ] T045 [P] Unit tests for APICredentials model in `tests/unit/test_api_credentials.py`
- [ ] T046 [P] Unit tests for ConfigurationManager methods in `tests/unit/test_configuration_manager.py`
- [ ] T047 [P] Unit tests for configuration validation logic in `tests/unit/test_config_validation.py`
- [ ] T048 [P] Unit tests for file operations and error handling in `tests/unit/test_config_file_ops.py`

### Performance and Security
- [ ] T049 [P] Performance tests for <100ms loading requirement in `tests/performance/test_config_performance.py`
- [ ] T050 [P] Security tests for file permissions and API key handling in `tests/integration/test_config_security.py`
- [ ] T051 [P] File size validation for 1MB limit in configuration manager
- [ ] T052 File permission enforcement for .env files (chmod 600)
- [ ] T053 Memory usage optimization for configuration caching

### Documentation and Error Handling
- [ ] T054 [P] Add comprehensive error messages with actionable suggestions
- [ ] T055 [P] Update UI strings for configuration workflow in `src/hlpr/config/ui_strings.py`
- [ ] T056 [P] Add configuration examples and help text
- [ ] T057 Remove any code duplication in configuration handling
- [ ] T058 Run quickstart validation scenarios from `quickstart.md`

## Dependencies

### Critical Path Dependencies
- **Setup Phase**: T001 (PyYAML) blocks all file operations
- **Tests Phase**: T004-T014 must fail before T015-T043
- **Models Phase**: T015-T020 block T021-T028 (manager needs models)
- **Manager Phase**: T021-T028 block T029-T033 (CLI needs manager)
- **Integration Phase**: T038-T043 require T021-T033 complete

### File-Level Dependencies (Sequential)
- **`src/hlpr/config/models.py`**: T015→T016→T017→T018→T019→T020
- **`src/hlpr/config/manager.py`**: T021→T022→T023→T024→T025→T026→T027→T028
- **`src/hlpr/cli/config_commands.py`**: T029→T030→T031→T032→T033

### Independent Parallel Groups
- **Contract Tests**: T004-T008 (different test files)
- **Integration Tests**: T009-T014 (different test files)
- **Support Utilities**: T034-T037 (different files)
- **Unit Tests**: T044-T048 (different test files)
- **Performance/Security**: T049-T051 (different test files)

## Parallel Execution Examples

### Phase 3.2 - All Contract Tests
```bash
# Launch contract tests together (all different files):
Task: "Contract test hlpr config setup command in tests/contract/test_config_setup.py"
Task: "Contract test hlpr config show command in tests/contract/test_config_show.py"
Task: "Contract test hlpr config edit command in tests/contract/test_config_edit.py"
Task: "Contract test hlpr config reset command in tests/contract/test_config_reset.py"
Task: "Contract test hlpr config validate command in tests/contract/test_config_validate.py"
```

### Phase 3.3 - Support Utilities
```bash
# Launch utilities in parallel (different files):
Task: "Implement default configuration values in src/hlpr/config/defaults.py"
Task: "Implement configuration validation utilities in src/hlpr/config/validators.py"
Task: "Implement migration utilities in src/hlpr/config/migration.py"
Task: "Create configuration file templates with placeholder examples in src/hlpr/config/templates.py"
```

### Phase 3.5 - Unit Tests
```bash
# Launch unit tests together (different files):
Task: "Unit tests for UserConfiguration model in tests/unit/test_user_configuration.py"
Task: "Unit tests for APICredentials model in tests/unit/test_api_credentials.py"
Task: "Unit tests for ConfigurationManager in tests/unit/test_configuration_manager.py"
```

## Task Validation Checklist
*GATE: Verified before execution*

- [x] All contracts have corresponding contract tests (T004-T008)
- [x] All entities from data-model.md have model tasks (T015-T020)
- [x] All CLI commands from contracts have implementation tasks (T029-T033)
- [x] All user scenarios from quickstart.md have integration tests (T009-T014)
- [x] All tests come before corresponding implementation
- [x] Parallel tasks operate on different files
- [x] Each task specifies exact file path
- [x] Critical dependencies identified and documented
- [x] Performance requirements addressed (T049, T053)
- [x] Security requirements addressed (T050, T052)
- [x] Configuration examples addressed (T037)
- [x] File size validation addressed (T051)

## Notes
- **TDD Approach**: All tests (T004-T014) must be written and failing before implementation begins
- **File Safety**: [P] tasks only when operating on completely different files
- **Error Handling**: Graceful fallback and user-friendly error messages prioritized
- **Performance**: <100ms loading requirement validated in T048
- **Security**: File permissions and API key protection validated in T049-T050
- **Integration**: Seamless integration with existing hlpr CLI maintained throughout