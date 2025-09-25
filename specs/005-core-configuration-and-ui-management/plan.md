# Implementation Plan: Core Configuration and UI Management System

**Branch**: `005-core-configuration-ui` | **Date**: September 25, 2025 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-core-configuration-and-ui-management/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
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
Centralized configuration management system that provides a single source of truth for provider defaults, format options, and chunk size limits across all hlpr modules. Includes UI string externalization for maintainability, schema validation with corruption recovery, and configuration reset safety while preserving user data. Technical approach centers on creating `config/platform.py` with immutable constants, validation routines, and atomic fallback mechanisms.

## Technical Context
**Language/Version**: Python 3.11+  
**Primary Dependencies**: Pydantic for data validation, existing hlpr.config, hlpr.exceptions modules  
**Storage**: JSON configuration files in user home directory (~/.hlpr/), existing src/hlpr/config/ui_strings.py  
**Testing**: pytest with contract, integration, and unit test layers  
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows) with permission handling differences  
**Project Type**: single - extends existing hlpr CLI application  
**Performance Goals**: Configuration loading <100ms startup time, validation processing <10ms per config item  
**Constraints**: Backward compatibility with existing config.py, no breaking changes to current CLI interfaces, preserve user data during resets  
**Scale/Scope**: 5 providers × 4 formats × 20+ configuration options, UI strings for 10+ CLI modules, support for 100+ concurrent config validations

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Modular Architecture**: ✅ PASS
- Creates self-contained `config/platform.py` module with clear interfaces
- UI strings remain in separate `config/ui_strings.py` with no cross-dependencies
- Configuration validation is isolated from business logic
- No circular import dependencies introduced

**Testable Design**: ✅ PASS  
- Configuration loading/validation is pure function-based
- Corruption recovery mechanisms are testable with mock files
- UI string referential integrity can be validated independently
- All error conditions have deterministic test scenarios

**Incremental Development**: ✅ PASS
- Phase approach: Constants extraction → Validation → Recovery → UI strings
- Backward compatibility maintained with existing config.py
- Can be deployed in stages without breaking existing functionality
- Existing UI strings can be migrated incrementally

**Post-Design Re-evaluation**: ✅ PASS
- Data model introduces no circular dependencies (platform.py → loader.py → recovery.py)
- Contract tests are isolated and independently testable
- Configuration recovery mechanisms maintain atomic operations
- UI string management preserves existing interface patterns

## Project Structure

### Documentation (this feature)
```
specs/005-core-configuration-and-ui-management/
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
- **Contract-based tasks**: Each API contract → failing contract test task [P]
- **Entity-based tasks**: Each data model entity → model implementation task [P]
- **Feature-based tasks**: Each functional requirement → integration test task
- **Infrastructure tasks**: Configuration loading, validation, recovery mechanisms

**Specific Task Categories**:
1. **Platform Constants** (4 tasks): Extract constants, create PlatformDefaults class, add validation, create unit tests
2. **Configuration Loading** (6 tasks): ConfigLoader implementation, environment override support, file loading, precedence handling, performance tests, integration tests
3. **Validation Engine** (5 tasks): ConfigValidator implementation, Pydantic models, error reporting, performance validation, contract tests
4. **Recovery System** (7 tasks): ConfigRecovery implementation, corruption detection, atomic backup, user data preservation, cross-platform permissions, recovery tests, quickstart validation
5. **UI String Management** (4 tasks): UIStringManager extension, referential integrity, migration helpers, validation tests
6. **Integration & Migration** (6 tasks): Backward compatibility, existing config.py integration, CLI module updates, end-to-end tests, performance validation, documentation updates

**Ordering Strategy**:
- **Phase A**: TDD foundation - Contract tests first (Tasks 1-8) [P]
- **Phase B**: Core models - PlatformDefaults, PlatformConfig, validation models (Tasks 9-16) [P] 
- **Phase C**: Services - ConfigLoader, ConfigValidator, ConfigRecovery (Tasks 17-24)
- **Phase D**: Integration - UI strings, CLI updates, backward compatibility (Tasks 25-32)
- **Phase E**: Validation - Quickstart scenarios, performance tests, migration validation (Tasks 33-36)

**Dependency Management**:
- Tasks marked [P] can execute in parallel (no shared dependencies)
- ConfigLoader depends on PlatformDefaults and ConfigValidator
- ConfigRecovery depends on ConfigValidator and file system permissions
- UI string updates depend on core configuration loading
- Integration tests depend on all core components

**Estimated Output**: 36 numbered, ordered tasks in tasks.md

**Success Metrics**:
- All contract tests fail initially (proving no implementation exists)
- Each task takes 1-4 hours of implementation time
- Tasks maintain atomic commits with clear success criteria
- Performance targets met: <100ms config loading, <10ms validation

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
- [x] Phase 0: Research complete (/plan command) - ✅ research.md generated
- [x] Phase 1: Design complete (/plan command) - ✅ data-model.md, contracts/, quickstart.md, agent context updated
- [x] Phase 2: Task planning complete (/plan command - describe approach only) - ✅ Strategy documented, 32-36 tasks estimated
- [ ] Phase 3: Tasks generated (/tasks command) - Ready for execution
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS - ✅ Modular, testable, incremental principles satisfied
- [x] Post-Design Constitution Check: PASS - ✅ No circular dependencies, atomic operations maintained
- [x] All NEEDS CLARIFICATION resolved - ✅ Technical context fully specified
- [x] Complexity deviations documented - ✅ No violations requiring justification

**Artifact Status**:
- [x] research.md - 6 technical decisions documented with alternatives
- [x] data-model.md - 6 core entities with validation rules and relationships  
- [x] contracts/api-contracts.md - 8 API contracts with success/failure scenarios
- [x] quickstart.md - 8 validation scenarios with performance benchmarks
- [x] GitHub Copilot context updated - New technical stack information added

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*