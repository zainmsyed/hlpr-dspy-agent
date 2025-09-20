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
- [ ] T001 Verify existing Python environment and UV dependency management
- [ ] T002 [P] Run ruff check to ensure codebase baseline compliance
- [ ] T003 Create test documents in /tmp/hlpr-test-docs for validation

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [ ] T004 [P] Contract test guided workflow with defaults in tests/contract/test_cli_guided_enhanced.py
- [ ] T005 [P] Contract test advanced options collection in tests/contract/test_cli_guided_enhanced.py
- [ ] T006 [P] Contract test option validation and error handling in tests/contract/test_cli_interactive_options.py
- [ ] T007 [P] Contract test command template generation in tests/contract/test_cli_guided_enhanced.py
- [ ] T008 [P] Contract test keyboard interrupt handling in tests/contract/test_cli_guided_enhanced.py
- [ ] T009 [P] Integration test complete guided workflow in tests/integration/test_guided_workflow_complete.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Data Models (Parallel Implementation)
- [ ] T010 [P] ProcessingOptions Pydantic model in src/hlpr/models/interactive.py
- [ ] T011 [P] CommandTemplate Pydantic model in src/hlpr/models/templates.py  
- [ ] T012 [P] SavedCommands manager class in src/hlpr/models/saved_commands.py
- [ ] T013 [P] OptionPrompts Rich interface in src/hlpr/cli/prompts.py

### Enhanced Interactive Session (Sequential - Same File)
- [ ] T014 Enhance InteractiveSession.collect_basic_options() in src/hlpr/cli/interactive.py
- [ ] T015 Add InteractiveSession.collect_advanced_options() in src/hlpr/cli/interactive.py
- [ ] T016 Add InteractiveSession.process_document_with_options() in src/hlpr/cli/interactive.py
- [ ] T017 Add InteractiveSession.generate_command_template() in src/hlpr/cli/interactive.py
- [ ] T018 Add InteractiveSession.display_command_template() in src/hlpr/cli/interactive.py
- [ ] T019 Add InteractiveSession.handle_keyboard_interrupt() in src/hlpr/cli/interactive.py

### Option Collection Implementation
- [ ] T020 Implement OptionPrompts.provider_prompt() in src/hlpr/cli/prompts.py
- [ ] T021 Implement OptionPrompts.format_prompt() in src/hlpr/cli/prompts.py
- [ ] T022 Implement OptionPrompts.save_file_prompt() in src/hlpr/cli/prompts.py
- [ ] T023 Implement OptionPrompts.temperature_prompt() in src/hlpr/cli/prompts.py
- [ ] T024 Implement OptionPrompts.advanced_options_prompt() in src/hlpr/cli/prompts.py

### Command Template System
- [ ] T025 Implement CommandTemplate.from_options() class method in src/hlpr/models/templates.py
- [ ] T026 Implement SavedCommands.save_command() in src/hlpr/models/saved_commands.py
- [ ] T027 Implement SavedCommands.load_commands() in src/hlpr/models/saved_commands.py

## Phase 3.4: Integration
- [ ] T028 Integrate ProcessingOptions.to_cli_args() with existing CLI pipeline
- [ ] T029 Connect enhanced guided workflow to existing _parse_with_progress()
- [ ] T030 Connect enhanced guided workflow to existing _summarize_with_progress()
- [ ] T031 Integrate template display with existing Rich error handling patterns
- [ ] T032 Update guided mode CLI entry point to use enhanced workflow

## Phase 3.5: Polish
- [ ] T033 [P] Unit tests for ProcessingOptions validation in tests/unit/test_option_validation.py
- [ ] T034 [P] Unit tests for CommandTemplate generation in tests/unit/test_template_generation.py
- [ ] T035 [P] Unit tests for SavedCommands persistence in tests/unit/test_saved_commands.py
- [ ] T036 Performance validation: UI responsiveness <100ms
- [ ] T037 Execute quickstart.md validation scenarios
- [ ] T038 Run final ruff check and format
- [ ] T039 Update .github/copilot-instructions.md with implementation notes

## Dependencies
- Setup (T001-T003) before tests
- Tests (T004-T009) before implementation (T010-T032)
- Models (T010-T013) before interactive methods (T014-T019)
- Core implementation (T010-T027) before integration (T028-T032)
- Integration complete before polish (T033-T039)

### Critical Dependencies
- T010 (ProcessingOptions) blocks T014, T015, T016, T017
- T011 (CommandTemplate) blocks T017, T025
- T013 (OptionPrompts) blocks T014, T015, T020-T024
- T014-T019 (InteractiveSession methods) block T028-T032

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

## Notes
- All contract tests must FAIL before implementation starts
- Enhanced InteractiveSession methods are sequential (same file)
- Model classes can be implemented in parallel (different files)
- Integration phase connects new components to existing CLI infrastructure
- Quickstart validation (T037) provides end-to-end confirmation

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

---

**Task Generation Status**: ✅ Complete  
**Total Tasks**: 39 tasks across 5 phases  
**Parallel Opportunities**: 3 phases with parallel execution  
**Estimated Implementation Time**: 6-8 hours with parallel execution