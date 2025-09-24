# Tasks: Robust Guided Workflow for Document Summarization

**Input**: Design documents from `/specs/004-guided-mode/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

````markdown
# Tasks: Robust Guided Workflow for Document Summarization

**Input**: Design documents from `/specs/004-guided-mode/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → LOADED: Python 3.11, typer/rich existing, pydantic validation
   → Structure: Single project (CLI enhancement to existing hlpr)
2. Load optional design documents:
   → data-model.md: 5 entities identified → model tasks
   → contracts/: 2 files → contract test tasks
   → research.md: Enhanced InteractiveSession approach
3. Generate tasks by category:
   → Setup: pydantic models, linting verification
   → Tests: contract tests for guided workflow
   → Core: interactive methods, option validation
   → Integration: CLI pipeline integration
   → Polish: unit tests, performance validation
4. Apply task rules:
   → Model creation [P] (different files)
   → Contract tests [P] (different files)
   → Interactive methods sequential (same file)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness: All FRs covered
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
Single project structure (existing hlpr codebase):
- **Models**: `src/hlpr/models/` 
- **CLI**: `src/hlpr/cli/`
- **Tests**: `tests/contract/`, `tests/integration/`, `tests/unit/`

## Phase 3.1: Setup
- [x] T001 Verify existing Python environment and UV dependency management
- [x] T002 [P] Run ruff check to ensure codebase baseline compliance
- [x] T003 Create test documents in /tmp/hlpr-test-docs for validation

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [x] T004 [P] Contract test guided workflow with defaults in tests/contract/test_cli_guided_enhanced.py
- [x] T005 [P] Contract test advanced options collection in tests/contract/test_cli_guided_enhanced.py
- [x] T006 [P] Contract test option validation and error handling in tests/contract/test_cli_interactive_options.py
- [x] T007 [P] Contract test command template generation in tests/contract/test_cli_guided_enhanced.py
- [x] T008 [P] Contract test keyboard interrupt handling in tests/contract/test_cli_guided_enhanced.py
- [x] T009 [P] Integration test complete guided workflow in tests/integration/test_guided_workflow_complete.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Data Models (Parallel Implementation)
- [x] T010 [P] ProcessingOptions Pydantic model in src/hlpr/models/interactive.py
- [x] T011 [P] CommandTemplate Pydantic model in src/hlpr/models/templates.py
- [x] T012 [P] SavedCommands manager class in src/hlpr/models/saved_commands.py
- [x] T013 [P] OptionPrompts Rich interface in src/hlpr/cli/prompts.py

### Enhanced Interactive Session (Sequential - Same File)
- [x] T014 Enhance InteractiveSession.collect_basic_options() in src/hlpr/cli/interactive.py
- [x] T015 Add InteractiveSession.collect_advanced_options() in src/hlpr/cli/interactive.py
- [x] T016 Add InteractiveSession.process_document_with_options() in src/hlpr/cli/interactive.py
- [x] T017 Add InteractiveSession.generate_command_template() in src/hlpr/cli/interactive.py
- [x] T018 Add InteractiveSession.display_command_template() in src/hlpr/cli/interactive.py
- [x] T019 Add InteractiveSession.handle_keyboard_interrupt() in src/hlpr/cli/interactive.py

### Option Collection Implementation
- [x] T020 Implement OptionPrompts.provider_prompt() in src/hlpr/cli/prompts.py
- [x] T021 Implement OptionPrompts.format_prompt() in src/hlpr/cli/prompts.py
- [x] T022 Implement OptionPrompts.save_file_prompt() in src/hlpr/cli/prompts.py
- [x] T023 Implement OptionPrompts.temperature_prompt() in src/hlpr/cli/prompts.py
- [x] T024 Implement OptionPrompts.advanced_options_prompt() in src/hlpr/cli/prompts.py

### Command Template System
- [x] T025 Implement CommandTemplate.from_options() class method in src/hlpr/models/templates.py
- [x] T026 Implement SavedCommands.save_command() in src/hlpr/models/saved_commands.py
- [x] T027 Implement SavedCommands.load_commands() in src/hlpr/models/saved_commands.py

## Phase 3.4: Integration
- [x] T028 Integrate ProcessingOptions.to_cli_args() with existing CLI pipeline
- [x] T029 Connect enhanced guided workflow to existing _parse_with_progress()
- [x] T030 Connect enhanced guided workflow to existing _summarize_with_progress()
- [x] T031 Integrate template display with existing Rich error handling patterns
- [x] T032 Update guided mode CLI entry point to use enhanced workflow

## Phase 3.5: Polish & Existing Validation
- [x] T033 [P] Unit tests for ProcessingOptions validation in tests/unit/test_option_validation.py
- [x] T034 [P] Unit tests for CommandTemplate generation in tests/unit/test_template_generation.py
- [x] T035 [P] Unit tests for SavedCommands persistence in tests/unit/test_saved_commands.py
- [x] T036 Performance validation: UI responsiveness <100ms
- [x] T037 Execute quickstart.md validation scenarios
- [x] T038 Run final ruff check and format
- [x] T039 Update .github/copilot-instructions.md with implementation notes

## Phase 3.6: Code Review Enhancements (HIGH PRIORITY)
**Based on comprehensive code review findings - addresses technical debt and UX improvements**

### User Experience & Accessibility Improvements (Parallel Implementation)
- [x] T040 [P] Enhance error messages with actionable guidance in src/hlpr/cli/validators.py
- [x] T041 [P] Add input validation feedback with retry logic in src/hlpr/cli/prompts.py
- [x] T042 [P] Implement in-app help and option explanations in src/hlpr/cli/help_display.py
- [x] T043 [P] Add provider/format descriptions to prompts in src/hlpr/cli/prompts.py

### Code Organization & Maintainability (Sequential - Related Files)
- [ ] T044 Create centralized configuration constants in src/hlpr/config/guided.py  <!-- in-progress: created config/guided.py -->
- [ ] T045 Implement custom exception hierarchy in src/hlpr/exceptions/guided.py
- [ ] T046 Externalize UI strings and messages in src/hlpr/config/ui_strings.py
- [ ] T047 Refactor InteractiveSession to reduce file size and responsibilities
- [ ] T048 Standardize method naming conventions across CLI components

### Recent updates (automated edit)
- [x] T044 Create centralized configuration constants in src/hlpr/config/guided.py (completed)
- [x] T045 Implement custom exception hierarchy in src/hlpr/exceptions/guided.py (completed)
- [x] T046 Externalize UI strings and messages in src/hlpr/config/ui_strings.py (completed)
- [x] T046.b Centralize provider messages in DSPy and validators (completed)

### Recommendations (next immediate steps for T044-T048)
- T044 (guided config): Create `src/hlpr/config/guided.py` with exported constants: ALLOWED_PROVIDERS, ALLOWED_FORMATS, DEFAULT_PROVIDER, DEFAULT_FORMAT, DEFAULT_CHUNK_SIZE, MAX_PROMPT_ATTEMPTS. Keep values in sync with `OptionPrompts` and `HelpDisplay`.
- T045 (exceptions): Add `src/hlpr/exceptions/guided.py` with a small hierarchy (GuidedError -> ValidationError, UserAbort, IOAccessError) used by prompts and validators.
- T046 (ui strings): Externalize user-facing strings into `src/hlpr/config/ui_strings.py` to make translation and testing simpler. Reference these from `validators.py`, `prompts.py`, and `help_display.py`.
- T047 (interactive refactor): Split `InteractiveSession` into `interactive/session.py` (or keep same file but extract helpers) to reduce size and separate responsibilities: option collection, execution orchestration, and template management.
- T048 (naming): Adopt `snake_case` for CLI method names and prefix interactive lifecycle methods with `run_`/`collect_` to standardize across the module.

### Feature Completeness (Parallel Implementation)  
- [x] T049 [P] Add user preferences persistence in src/hlpr/models/user_preferences.py
- [x] T050 [P] Implement template management CLI commands in src/hlpr/cli/template_commands.py
- [ ] T051 [P] Add interactive file picker/browser in src/hlpr/cli/file_picker.py
- [ ] T052 [P] Implement configuration reset functionality in src/hlpr/cli/config_commands.py

### Performance & Scalability Improvements (Parallel Implementation)
- [ ] T053 [P] Add async file operations for template saves in src/hlpr/models/saved_commands.py
- [ ] T054 [P] Implement progress indicators for all operations in src/hlpr/cli/rich_display.py
- [ ] T055 [P] Add memory-efficient document handling for guided mode
- [ ] T056 [P] Create batch processing support for guided workflow in src/hlpr/cli/batch_guided.py

### Security & Validation Enhancements (Parallel Implementation)
- [ ] T057 [P] Enhance input sanitization and path validation in src/hlpr/cli/validators.py
- [ ] T058 [P] Add comprehensive error taxonomy in src/hlpr/exceptions/guided.py
- [ ] T059 [P] Implement secure template storage with permissions check
- [ ] T060 [P] Add configuration file validation and recovery

## Phase 3.7: Enhanced Testing & Documentation
- [ ] T061 [P] Unit tests for enhanced error handling in tests/unit/test_error_handling_enhanced.py
- [ ] T062 [P] Unit tests for user preferences persistence in tests/unit/test_user_preferences.py
- [ ] T063 [P] Integration tests for template management in tests/integration/test_template_management.py
- [ ] T064 [P] Performance benchmarks for UI responsiveness in tests/performance/test_ui_performance.py
- [ ] T065 [P] Security tests for input validation in tests/security/test_input_validation.py
- [ ] T066 Create comprehensive user guide for enhanced guided mode in docs/guided-mode.md
- [ ] T067 Update CLI help documentation with new features
- [ ] T068 Create troubleshooting guide for common issues

## Dependencies
- Setup (T001-T003) before tests
- Tests (T004-T009) before implementation (T010-T032)
- Models (T010-T013) before interactive methods (T014-T019)
- Core implementation (T010-T027) before integration (T028-T032)
- Integration complete before polish (T033-T039)
- **Enhancement dependencies**: Core complete before enhancements (T040-T060)
- **Testing dependencies**: Enhancements before enhanced testing (T061-T068)

### Critical Dependencies
- T010 (ProcessingOptions) blocks T014, T015, T016, T017
- T011 (CommandTemplate) blocks T017, T025
- T013 (OptionPrompts) blocks T014, T015, T020-T024
- T014-T019 (InteractiveSession methods) block T028-T032
- **Enhancement blocking**: T032 (existing integration) blocks T040-T060
- T044-T046 (config/exceptions/strings) block T047-T048 (refactoring)
- T049 (user preferences) blocks T052 (config commands)

## Parallel Execution Examples

### Phase 3.2: Contract Tests (All Parallel)
```bash
# Launch T004-T009 together:
Task: "Contract test guided workflow with defaults in tests/contract/test_cli_guided_enhanced.py"
Task: "Contract test advanced options collection in tests/contract/test_cli_guided_enhanced.py" 
Task: "Contract test option validation in tests/contract/test_cli_interactive_options.py"
Task: "Contract test command template generation in tests/contract/test_cli_guided_enhanced.py"
Task: "Integration test complete guided workflow in tests/integration/test_guided_workflow_complete.py"
```

### Phase 3.3: Data Models (All Parallel)
```bash
# Launch T010-T013 together:
Task: "ProcessingOptions Pydantic model in src/hlpr/models/interactive.py"
Task: "CommandTemplate Pydantic model in src/hlpr/models/templates.py"
Task: "SavedCommands manager class in src/hlpr/models/saved_commands.py"
Task: "OptionPrompts Rich interface in src/hlpr/cli/prompts.py"
```

### Phase 3.5: Unit Tests (All Parallel)
```bash
# Launch T033-T035 together:
Task: "Unit tests for ProcessingOptions validation in tests/unit/test_option_validation.py"
Task: "Unit tests for CommandTemplate generation in tests/unit/test_template_generation.py" 
Task: "Unit tests for SavedCommands persistence in tests/unit/test_saved_commands.py"
```

### Phase 3.6: Code Review Enhancements (Selected Parallel Groups)
```bash
# UX Improvements (T040-T043) - All parallel:
Task: "Enhance error messages with actionable guidance in src/hlpr/cli/validators.py"
Task: "Add input validation feedback with retry logic in src/hlpr/cli/prompts.py"
Task: "Implement in-app help and option explanations in src/hlpr/cli/help_display.py"
Task: "Add provider/format descriptions to prompts in src/hlpr/cli/prompts.py"

# Feature Completeness (T049-T052) - All parallel:
Task: "Add user preferences persistence in src/hlpr/models/user_preferences.py"
Task: "Implement template management CLI commands in src/hlpr/cli/template_commands.py"
Task: "Add interactive file picker/browser in src/hlpr/cli/file_picker.py"
Task: "Implement configuration reset functionality in src/hlpr/cli/config_commands.py"

# Performance & Security (T053-T060) - All parallel:
Task: "Add async file operations for template saves in src/hlpr/models/saved_commands.py"
Task: "Implement progress indicators for all operations in src/hlpr/cli/rich_display.py"
Task: "Add memory-efficient document handling for guided mode"
Task: "Create batch processing support for guided workflow in src/hlpr/cli/batch_guided.py"
```

### Phase 3.7: Enhanced Testing (All Parallel)
```bash
# Launch T061-T065 together:
Task: "Unit tests for enhanced error handling in tests/unit/test_error_handling_enhanced.py"
Task: "Unit tests for user preferences persistence in tests/unit/test_user_preferences.py"
Task: "Integration tests for template management in tests/integration/test_template_management.py"
Task: "Performance benchmarks for UI responsiveness in tests/performance/test_ui_performance.py"
Task: "Security tests for input validation in tests/security/test_input_validation.py"
```

## Functional Requirements Coverage

### Contract Test Mapping
- **FR-001** (Interactive guided mode): T004, T005, T009
- **FR-002** (Two-tier options): T005, T006
- **FR-003** (Default values): T004, T006
- **FR-004** (Existing pipeline reuse): T009, T029, T030
- **FR-005** (Progress display): T009, T029, T030
- **FR-006** (Output formats): T006, T009
- **FR-007** (Command templates): T007, T017, T025
- **FR-008** (Error handling): T006, T008
- **FR-009** (Keyboard interrupts): T008, T019
- **FR-010** (CLI function reuse): T029, T030, T031
- **FR-011** (Atomic file operations): T026, T027
- **FR-012** (Basic options): T004, T014, T020-T022
- **FR-013** (Advanced options): T005, T015, T023-T024

### Implementation Task Mapping
- **Models**: T010 (ProcessingOptions), T011 (CommandTemplate), T012 (SavedCommands)
- **Interactive UI**: T013 (OptionPrompts), T014-T019 (InteractiveSession methods)
- **CLI Integration**: T028-T032 (pipeline integration, entry point)
- **Validation**: T033-T039 (unit tests, performance, documentation)
- **Enhancement Features**: T040-T060 (code review recommendations)
- **Enhanced Testing**: T061-T068 (comprehensive validation and documentation)

### Code Review Recommendations Coverage
- **UX Improvements**: T040-T043 (error messages, validation feedback, help, descriptions)
- **Code Organization**: T044-T048 (config, exceptions, strings, refactoring, naming)
- **Feature Completeness**: T049-T052 (preferences, templates, file picker, config)
- **Performance**: T053-T056 (async ops, progress, memory, batch processing)
- **Security**: T057-T060 (input sanitization, error taxonomy, secure storage, validation)
- **Testing**: T061-T065 (enhanced error handling, preferences, templates, performance, security)
- **Documentation**: T066-T068 (user guide, CLI help, troubleshooting)

## Notes
- All contract tests must FAIL before implementation starts
- Enhanced InteractiveSession methods are sequential (same file)
- Model classes can be implemented in parallel (different files)
- Integration phase connects new components to existing CLI infrastructure
- **Code Review Integration**: Tasks T040-T068 address all high-priority code review findings
- **Phased Approach**: Core functionality first, then enhancements, then comprehensive testing
- Quickstart validation (T037) provides end-to-end confirmation
- **Enhancement Focus**: Significant UX improvements, code organization, and feature completeness

## Task Generation Rules Applied
1. **From Contracts**: Each contract requirement → contract test task [P]
2. **From Data Model**: Each entity → model creation task [P] 
3. **From Interactive Session**: Each method → implementation task (sequential)
4. **From User Stories**: Quickstart scenarios → integration test [P]
5. **Ordering**: Setup → Tests → Models → Services → Integration → Polish
6. **Parallel**: Different files with no shared dependencies

## Validation Checklist
*GATE: Checked before task execution begins*

- [x] All 13 functional requirements have corresponding tests
- [x] All 5 entities have model creation tasks
- [x] All tests come before implementation (TDD approach)
- [x] Parallel tasks are truly independent (different files)
- [x] Each task specifies exact file path
- [x] No [P] task modifies same file as another [P] task
- [x] Dependencies properly documented and enforced
- [x] **Code review recommendations fully integrated as actionable tasks**
- [x] **Enhancement tasks address identified technical debt and UX issues**
- [x] **Comprehensive testing strategy includes performance and security validation**

---

**Task Generation Status**: ✅ Complete with Code Review Integration  
**Total Tasks**: 68 tasks across 7 phases  
**Parallel Opportunities**: 6 phases with parallel execution  
**Core Implementation**: Complete (T001-T039)  
**Enhancement Implementation**: Ready for execution (T040-T068)  
**Estimated Enhancement Time**: 8-12 hours with parallel execution  
**Priority**: High-priority code review recommendations integrated as tasks T040-T060
````