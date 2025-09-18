# Implementation Plan: Enhanced CLI/TUI for Document Summarization

**Branch**: `003-cli-tui-of` | **Date**: September 18, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/home/zain/Documents/coding/hlpr/specs/003-cli-tui-of/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
4. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
5. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, or `GEMINI.md` for Gemini CLI).
6. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
7. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
8. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Enhanced CLI/TUI experience for document summarization with two main modes: guided interactive mode for beginners via `hlpr summarize` and direct power-user commands like `hlpr summarize document <file>`. Uses Rich for beautiful progress bars, color-coded panels, and Rich terminal output, with Typer for robust CLI structure. Supports multiple output formats, batch processing, and comprehensive error handling with fallback mechanisms.

## Technical Context
**Language/Version**: Python 3.11  
**Primary Dependencies**: typer, rich, dspy, pydantic, pathlib  
**Storage**: N/A (stateless CLI processing)  
**Testing**: pytest with contract/integration/unit test structure  
**Target Platform**: Linux/macOS/Windows CLI environments  
**Project Type**: single (enhancing existing CLI structure)  
**Performance Goals**: <2s startup time, responsive progress feedback, graceful handling of 100MB+ files  
**Constraints**: Must work with local LLM providers without timeouts, backward compatible with existing CLI  
**Scale/Scope**: Single-user CLI tool, supports file sizes up to 500MB with chunking, 20 CLI options/flags

**User-provided implementation details**: Using rich and typer for beautiful, interactive CLI/TUI experience

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**:
- Projects: 1 (enhancing existing CLI within single project structure)
- Using framework directly? Yes (typer and rich used directly, no wrapper classes)
- Single data model? Yes (existing Document model, adding CLI interaction models)
- Avoiding patterns? Yes (direct CLI command functions, no unnecessary abstractions)

**Architecture**:
- EVERY feature as library? Yes (interactive prompts, rich formatting as reusable modules)
- Libraries listed: 
  - `cli.interactive` - guided mode prompts and workflows
  - `cli.rich_display` - formatted output panels and progress bars
  - `cli.validators` - input validation and error handling
- CLI per library: Enhanced `hlpr summarize` command with guided and direct modes
- Library docs: Will document in existing structure (README.md usage examples)

**Testing (NON-NEGOTIABLE)**:
- RED-GREEN-Refactor cycle enforced? Yes (contract tests will fail first)
- Git commits show tests before implementation? Yes (following existing pattern)
- Order: Contract→Integration→E2E→Unit strictly followed? Yes
- Real dependencies used? Yes (actual file system, real Rich console)
- Integration tests for: Enhanced CLI workflows, interactive prompts, Rich output formatting
- FORBIDDEN: Implementation before test, skipping RED phase

**Observability**:
- Structured logging included? Yes (using existing hlpr.logging_utils)
- Frontend logs → backend? N/A (CLI-only feature)
- Error context sufficient? Yes (Rich error panels with actionable suggestions)

**Versioning**:
- Version number assigned? Extends current hlpr version
- BUILD increments on every change? Yes (following existing pattern)
- Breaking changes handled? No breaking changes (additive CLI enhancements)

**Status**: ✅ PASS - No violations identified
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
# Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure]
```

**Structure Decision**: [DEFAULT to Option 1 unless Technical Context indicates web/mobile app]

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
   - Run `/scripts/update-agent-context.sh [claude|gemini|copilot]` for your AI assistant
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `/templates/tasks-template.md` as base structure
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- CLI contract validation → contract test tasks [P]
- Each data model entity → model implementation tasks [P]
- Interactive flow contracts → integration test tasks
- Progress display contracts → Rich integration tasks [P]
- Error handling contracts → error handling implementation tasks
- Output format contracts → renderer implementation tasks [P]
- Quickstart scenarios → validation test tasks

**Ordering Strategy**:
- **Phase 1**: Contract tests (must fail initially) - 8 tasks
- **Phase 2**: Core models and data structures - 6 tasks [P]
- **Phase 3**: CLI infrastructure (interactive, rich_display, validators) - 9 tasks
- **Phase 4**: Integration components (batch processing, renderers) - 7 tasks [P]
- **Phase 5**: Error handling and edge cases - 5 tasks
- **Phase 6**: Integration tests and quickstart validation - 8 tasks

**Task Dependencies**:
- Contract tests → Independent [P]
- Data models → Independent [P]  
- CLI interactive → Depends on data models
- Rich display → Depends on data models
- Batch processing → Depends on CLI infrastructure
- Renderers → Independent [P]
- Integration tests → Depends on all implementation tasks

**Estimated Output**: 43 numbered, ordered tasks organized into 6 phases with clear dependencies

**Key Task Categories**:
1. **Contract Tests**: Failing tests for all CLI interactions
2. **Models**: InteractiveSession, ProcessingState, OutputPreferences, etc.
3. **CLI Infrastructure**: Guided mode, Rich formatting, input validation
4. **Processing Logic**: Batch handling, progress tracking, result management
5. **Output**: Format-specific renderers for rich/txt/md/json
6. **Validation**: Integration tests matching quickstart scenarios

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
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [x] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*