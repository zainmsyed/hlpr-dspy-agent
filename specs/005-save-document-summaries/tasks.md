# Tasks: Save Document Summaries in Organized Folder Structure

**Input**: Design documents from `/specs/005-save-document-summaries/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Tech stack: Python 3.11+, typer, rich, pathlib, os
   → Structure: Single CLI application enhancement
2. Load design documents:
   → data-model.md: OutputPath, OrganizedStorage, SummaryFileInfo entities
   → contracts/: CLI spec and API spec enhancements
   → research.md: Path resolution and default format decisions
   → quickstart.md: 12 validation test scenarios
3. Generate tasks by category:
   → Setup: linting, dependencies validation
   → Tests: CLI contract tests, integration tests (TDD approach)
   → Core: utility modules, CLI enhancements, model extensions
   → Integration: error handling, path resolution
   → Polish: quickstart validation, cleanup
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Tasks numbered T001-T020
6. Focus on CLI enhancement with organized storage
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
**Single project structure** (from plan.md):
- Core implementation: `src/hlpr/cli/summarize.py`, `src/hlpr/io/organized_storage.py`
- Models: `src/hlpr/models/output_preferences.py`
- Tests: `tests/contract/`, `tests/integration/`, `tests/unit/`

## Phase 3.1: Setup
- [ ] T001 Validate existing dependencies (typer, rich, pathlib) and linting setup with ruff
- [ ] T002 [P] Create directory structure for new modules: `src/hlpr/io/` and enhanced model files

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [ ] T003 [P] Contract test CLI organized storage behavior in `tests/contract/test_cli_organized_storage.py`
- [ ] T004 [P] Contract test CLI custom path bypass in `tests/contract/test_cli_custom_path.py`
- [ ] T005 [P] Contract test API enhanced endpoint in `tests/contract/test_api_organized_storage.py`
- [ ] T006 [P] Integration test directory creation and permissions in `tests/integration/test_directory_creation.py`
- [ ] T007 [P] Integration test path resolution logic in `tests/integration/test_path_resolution.py`
- [ ] T008 [P] Integration test error handling scenarios in `tests/integration/test_storage_errors.py`

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [ ] T009 [P] Create OutputPath model in `src/hlpr/models/output_path.py`
- [ ] T010 [P] Create OrganizedStorage utility class in `src/hlpr/io/organized_storage.py`
- [ ] T011 [P] Create SummaryFileInfo model in `src/hlpr/models/summary_file_info.py`
- [ ] T012 [P] Enhance OutputPreferences model in `src/hlpr/models/output_preferences.py`
- [ ] T013 Enhance `_determine_output_path()` function in `src/hlpr/cli/summarize.py`
- [ ] T014 Enhance `_save_summary()` function in `src/hlpr/cli/summarize.py`
- [ ] T015 Update default format from txt to md in `src/hlpr/cli/summarize.py`

## Phase 3.4: Integration & Error Handling
- [ ] T016 Implement comprehensive error handling for permission denied in organized storage utilities
- [ ] T017 Implement path validation and disk space error handling in organized storage utilities
- [ ] T018 Update API endpoint `/summarize/document` with organized storage options in `src/hlpr/api/summarize.py`

## Phase 3.5: Polish & Validation
- [ ] T019 [P] Unit tests for path resolution edge cases in `tests/unit/test_path_resolution.py`
- [ ] T020 [P] Unit tests for directory creation utilities in `tests/unit/test_organized_storage.py`
- [ ] T021 Execute quickstart validation scenarios from `quickstart.md`
- [ ] T022 Remove any code duplication and verify DRY principles
- [ ] T023 Update documentation and help text for enhanced CLI options

## Dependencies
- Setup (T001-T002) before everything
- Tests (T003-T008) before implementation (T009-T018)
- T009-T012 (models) before T013-T015 (CLI integration)
- T010 (OrganizedStorage) blocks T013-T014 (CLI functions using utilities)
- T013-T015 before T016-T018 (core before integration)
- Implementation complete before polish (T019-T023)

## Parallel Execution Examples

### Phase 3.2 - All Test Files (Parallel)
```bash
# Launch T003-T008 together (different test files):
Task: "Contract test CLI organized storage behavior in tests/contract/test_cli_organized_storage.py"
Task: "Contract test CLI custom path bypass in tests/contract/test_cli_custom_path.py"  
Task: "Contract test API enhanced endpoint in tests/contract/test_api_organized_storage.py"
Task: "Integration test directory creation in tests/integration/test_directory_creation.py"
Task: "Integration test path resolution in tests/integration/test_path_resolution.py"
Task: "Integration test error handling in tests/integration/test_storage_errors.py"
```

### Phase 3.3 - Model Creation (Parallel)
```bash
# Launch T009-T012 together (different model files):
Task: "Create OutputPath model in src/hlpr/models/output_path.py"
Task: "Create OrganizedStorage utility in src/hlpr/io/organized_storage.py"
Task: "Create SummaryFileInfo model in src/hlpr/models/summary_file_info.py"
Task: "Enhance OutputPreferences model in src/hlpr/models/output_preferences.py"
```

### Phase 3.5 - Unit Tests (Parallel)
```bash
# Launch T019-T020 together (different unit test files):
Task: "Unit tests for path resolution in tests/unit/test_path_resolution.py" 
Task: "Unit tests for directory creation in tests/unit/test_organized_storage.py"
```

## Key Implementation Notes

### T003-T008: Test Requirements (TDD)
- **T003**: Test `hlpr summarize document file.pdf --save` creates `hlpr/summaries/documents/file_summary.md`
- **T004**: Test `hlpr summarize document file.pdf --save --output /custom/path.txt` uses exact path
- **T005**: Test API `organized_storage: true` parameter and response `storage_info`
- **T006**: Test directory creation, permissions, disk space scenarios
- **T007**: Test path resolution for various document names and formats
- **T008**: Test permission denied, invalid paths, disk full error scenarios

### T009-T012: Core Models
- **T009**: `OutputPath` with path resolution logic and validation
- **T010**: `OrganizedStorage` with directory creation and path utilities
- **T011**: `SummaryFileInfo` for metadata tracking
- **T012**: Enhanced `OutputPreferences` with organized storage options

### T013-T015: CLI Integration
- **T013**: Modify `_determine_output_path()` to use `OrganizedStorage` utilities
- **T014**: Modify `_save_summary()` to create directories and handle errors
- **T015**: Change default format parameter from "txt" to "md"

### T016-T018: Error Handling & API
- **T016**: Comprehensive error handling with user-friendly messages
- **T017**: Path validation and disk space error recovery
- **T018**: API endpoint enhancement with storage options

## Task Generation Rules Applied

1. **From CLI Contract**: T003-T004 (CLI behavior tests) → T013-T015 (CLI implementation)
2. **From API Contract**: T005 (API test) → T018 (API implementation)  
3. **From Data Model**: T009-T012 (each entity → model task, all [P])
4. **From Quickstart**: T006-T008 (integration tests) → T021 (validation)
5. **From Research**: T015 (default format change), T016-T017 (error handling decisions)

## Validation Checklist
*GATE: Checked before task execution*

- [x] All contracts have corresponding tests (T003-T005)
- [x] All entities have model tasks (T009-T012) 
- [x] All tests come before implementation (T003-T008 before T009-T018)
- [x] Parallel tasks truly independent (different files)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] TDD approach: failing tests before any implementation
- [x] Backward compatibility preserved in all changes

*Tasks complete: 23 numbered tasks ready for execution following TDD principles*