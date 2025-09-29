
# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

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
Interactive save prompt using Rich when `--save` flag is not provided. After displaying summary, prompts user to confirm save (default yes), choose format (md/txt/json, default md), and select destination path (organized storage default). Privacy-first: no auto-save in non-interactive contexts unless explicitly opted-in via `--save` flag or `HLPR_AUTO_SAVE=true` environment variable. Uses atomic writes and timestamp suffixes to avoid overwriting existing files.

## Technical Context
**Language/Version**: Python 3.11+  
**Primary Dependencies**: `rich` (prompts), `typer` (CLI framework), existing `hlpr.io.atomic` (atomic writes)  
**Storage**: Local filesystem via organized storage paths and atomic writes  
**Testing**: pytest with monkeypatching for Rich prompts and TTY detection  
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows)  
**Project Type**: single - CLI-focused feature enhancement  
**Performance Goals**: Interactive response time <100ms for prompts  
**Constraints**: Privacy-first (no auto-save without consent), atomic writes required, backwards compatibility with existing `--save` flag  
**Scale/Scope**: Single feature enhancement affecting 2 CLI commands (document + meeting summarization)

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Privacy-First Design**: Feature respects "No Data Retention" principle by making auto-save opt-in only in non-interactive contexts
✅ **CLI-First Experience**: Enhances CLI with Rich prompts for better interactive experience  
✅ **Modern Tooling**: Uses existing `rich` dependency and follows `uv` package management  
✅ **DRY Code Practice**: Reuses existing `atomic_write_text`, `_format_summary_content`, and organized storage logic  
✅ **Modular Architecture**: Self-contained enhancement to CLI module without affecting core AI logic  

**No constitutional violations detected**

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
│   └── summarize.py        # Modified: add _interactive_save_flow() helper
├── io/
│   └── atomic.py            # Existing: atomic_write_text() used for safe writes
├── models/
└── config/

tests/
├── contract/
│   └── test_cli_save_behavior.py     # New: contract-level CLI behavior tests
├── unit/
│   ├── test_cli_save_prompt_default.py    # New: default save behavior
│   ├── test_cli_save_prompt_decline.py    # New: decline save behavior  
│   ├── test_cli_save_prompt_json.py       # New: JSON format tests
│   ├── test_cli_save_prompt_non_tty.py    # New: non-interactive opt-in tests
│   ├── test_cli_save_prompt_collision.py  # New: timestamp suffix tests
│   └── test_cli_save_error_handling.py    # New: StorageError mapping tests
└── integration/
```

**Structure Decision**: Single project layout. Feature adds interactive prompts to existing CLI commands in `src/hlpr/cli/summarize.py` and comprehensive test coverage in `tests/unit/` and `tests/contract/`. No new modules required - enhancement of existing CLI functionality.

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
- Each contract → contract test task [P] (T002)
- Rich prompt behaviors → unit test tasks [P] (T003-T006, T009, T011)
- Implementation tasks: CLI enhancement (T007), timestamp helper (T008)
- Support tasks: setup (T001), docs (T010), polish (T012)

**Ordering Strategy**:
- TDD order: Tests before implementation 
- Setup first (T001), then parallel test creation (T002-T006, T009, T011)
- Implementation after tests (T007-T008), then docs and polish
- Mark [P] for parallel execution (independent test files)

**Estimated Output**: 12 numbered, ordered tasks in tasks.md (completed)

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
- [ ] Phase 0: Research complete (/plan command)
- [ ] Phase 1: Design complete (/plan command)
- [ ] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [ ] Initial Constitution Check: PASS
- [ ] Post-Design Constitution Check: PASS
- [ ] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
