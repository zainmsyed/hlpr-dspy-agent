
# Implementation Plan: Save Document Summaries in Organized Folder Structure

**Branch**: `005-save-document-summaries` | **Date**: September 28, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-save-document-summaries/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Implement organized folder structure for document summary storage. When users save summaries via `--save` flag, automatically create and use `hlpr/summaries/documents/` folder structure relative to current working directory. Maintain backward compatibility by respecting exact custom paths when `--output` is specified. Default file format changed to Markdown (.md).

## Technical Context
**Language/Version**: Python 3.11+  
**Primary Dependencies**: typer, rich, pathlib, os (standard library modules)  
**Storage**: File system operations (directory creation, file writing)  
**Testing**: pytest with contract tests for CLI behavior  
**Target Platform**: Cross-platform (Linux, macOS, Windows)
**Project Type**: single - CLI application enhancement  
**Performance Goals**: Instant folder creation, <100ms path resolution  
**Constraints**: Must maintain backward compatibility with existing `--output` parameter  
**Scale/Scope**: Individual user workflow enhancement, no concurrent access patterns

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Initial Check**:
**Modular Architecture**: ✅ PASS - Enhances existing CLI module without adding new modules  
**Privacy-First Design**: ✅ PASS - No network operations, purely local file system enhancement  
**CLI-First Experience**: ✅ PASS - Improves CLI user experience with organized storage  
**DSPy Integration**: ✅ PASS - No changes to AI workflows, storage enhancement only  
**Modern Tooling**: ✅ PASS - Uses standard library, maintains UV/Ruff compliance  
**DRY Code Practice**: ✅ PASS - Enhances existing `_save_summary()` function, no duplication

**Post-Design Check**:
**Modular Architecture**: ✅ PASS - New `organized_storage.py` utility module, clean separation  
**Privacy-First Design**: ✅ PASS - All operations local file system, no data transmission  
**CLI-First Experience**: ✅ PASS - Enhanced CLI with better UX, clear error messages  
**DSPy Integration**: ✅ PASS - No modifications to AI pipelines or DSPy workflows  
**Modern Tooling**: ✅ PASS - Pathlib usage, type hints, Pydantic models planned  
**DRY Code Practice**: ✅ PASS - Centralized path resolution, reusable utilities

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
src/hlpr/
├── cli/
│   └── summarize.py        # Enhanced _save_summary() and _determine_output_path()
├── io/
│   └── organized_storage.py # NEW: Folder creation and path resolution utilities
└── models/
    └── output_preferences.py # NEW: Enhanced output configuration

tests/
├── contract/
│   └── test_cli_summarize_document.py # Enhanced with folder structure tests
├── integration/
│   └── test_organized_storage.py      # NEW: File system integration tests
└── unit/
    ├── test_organized_storage.py      # NEW: Unit tests for storage utilities
    └── test_output_preferences.py     # NEW: Unit tests for preferences model
```

**Structure Decision**: Single project enhancement - modifying existing CLI module and adding supporting utilities. Primary changes in `src/hlpr/cli/summarize.py` with new utility modules for organized storage functionality.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh copilot`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- **Contract Tests**: CLI behavior with/without `--output`, organized structure creation [P]
- **Utility Modules**: `organized_storage.py` for path resolution and directory creation [P]
- **Model Extensions**: Enhanced `OutputPreferences` for organized storage config [P]
- **CLI Enhancements**: Modified `_save_summary()` and `_determine_output_path()` functions
- **Integration Tests**: File system operations, error handling scenarios
- **Quickstart Validation**: End-to-end testing following quickstart.md steps

**Ordering Strategy**:
- **Phase 1**: Contract tests (TDD approach) - Define expected behavior
- **Phase 2**: Utility modules - Core path resolution and directory creation
- **Phase 3**: Model enhancements - Configuration and data structures  
- **Phase 4**: CLI integration - Modify existing CLI functions
- **Phase 5**: Error handling - Comprehensive error scenarios
- **Phase 6**: Integration testing - End-to-end validation
- Mark [P] for parallel execution where modules are independent

**Estimated Output**: 15-20 numbered, ordered tasks in tasks.md

**Key Implementation Areas**:
1. **Path Resolution Logic**: `determine_output_path()` function enhancement
2. **Directory Creation**: `ensure_summary_directories()` utility function
3. **Error Handling**: Permission, disk space, and validation errors
4. **CLI Integration**: Seamless integration with existing `--save` workflow
5. **Backward Compatibility**: Preserve all existing behaviors exactly

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning approach described (/plan command)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] No complexity deviations needed

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
