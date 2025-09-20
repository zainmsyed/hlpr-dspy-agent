# Implementation Plan: Robust Guided Workflow for Document Summarization

**Branch**: `004-guided-mode` | **Date**: September 20, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-guided-mode/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → LOADED: Feature spec analyzed with 13 functional requirements
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Project Type: single (CLI enhancement)
   → Structure Decision: Option 1 (existing hlpr structure)
3. Fill the Constitution Check section based on constitution document
   → All requirements align with modular architecture and CLI-first principles
4. Evaluate Constitution Check section
   → No violations detected - all requirements support constitutional principles
   → Update Progress Tracking: Initial Constitution Check PASS
5. Execute Phase 0 → research.md
   → No NEEDS CLARIFICATION markers in spec - proceeding
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, copilot-instructions.md
7. Re-evaluate Constitution Check section
   → Post-design check will be performed after Phase 1
   → Update Progress Tracking: Pending Post-Design Constitution Check
8. Plan Phase 2 → Task generation approach documented
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Transform the current simulation-only guided mode (`hlpr summarize guided`) into a fully functional interactive document summarization experience. The implementation will reuse existing CLI functions while adding interactive option collection, real-time progress tracking, and command template generation. Key focus on maintaining constitutional compliance with modular architecture and CLI-first principles.

## Technical Context
**Language/Version**: Python 3.11  
**Primary Dependencies**: typer, rich (existing), pydantic for option validation  
**Storage**: File system for saved command templates (~/.hlpr/saved_commands.json)  
**Testing**: pytest (existing test infrastructure)  
**Target Platform**: Linux CLI (cross-platform compatible)
**Project Type**: single (CLI enhancement to existing hlpr structure)  
**Performance Goals**: Interactive response <100ms for UI updates, maintain existing summarization performance  
**Constraints**: Must reuse existing CLI functions, maintain backward compatibility, no new major dependencies  
**Scale/Scope**: Single-user CLI enhancement, 5-10 new interactive methods, ~200 LOC total

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Modular Architecture - ✅ COMPLIANT
- **Standalone Module**: Interactive workflow contained in `src/hlpr/cli/interactive.py`
- **Clear Separation**: Interactive layer separate from core summarization logic
- **Testable Interface**: Each interactive method independently testable
- **Existing Integration**: Reuses established CLI and document processing modules

### II. Privacy-First Design - ✅ COMPLIANT  
- **Local Processing**: Interactive workflow doesn't change document processing
- **No Data Retention**: Command templates stored locally, no personal content
- **Existing Security**: Leverages existing secure credential and processing patterns

### III. CLI-First Experience - ✅ COMPLIANT
- **Interactive Mode Enhancement**: Improves existing guided workflow capability
- **Rich Output**: Uses existing Rich display infrastructure
- **Error Handling**: Extends existing CLI error handling patterns
- **Configuration**: Uses existing configuration management

### IV. DSPy Integration & Optimization - ✅ COMPLIANT
- **No Changes**: Interactive layer doesn't modify existing DSPy workflows
- **Provider Support**: Uses existing provider flexibility and timeout policies
- **Error Recovery**: Leverages existing retry mechanisms

### V. Modern Tooling & Quality - ✅ COMPLIANT
- **UV Management**: No new dependencies requiring UV addition
- **Ruff Compliance**: All new code will follow existing standards
- **Type Hints**: Pydantic models for interactive options
- **Existing Infrastructure**: Builds on established patterns

## Project Structure

### Documentation (this feature)
```
specs/004-guided-mode/
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
│   ├── interactive.py   # Enhanced guided workflow
│   ├── validators.py    # Input validation helpers
│   └── templates.py     # Command template generation
└── lib/

tests/
├── contract/
│   ├── test_cli_guided_enhanced.py
│   └── test_cli_interactive_options.py
├── integration/
│   └── test_guided_workflow_complete.py
└── unit/
    ├── test_interactive_session.py
    └── test_option_validation.py
```

**Structure Decision**: Option 1 - Single project structure fits CLI enhancement perfectly

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - All technical aspects clearly defined in existing codebase
   - Interactive UX patterns already established in current CLI
   - No external research required - leveraging existing patterns

2. **Generate and dispatch research agents**:
   ```
   Task: "Analyze existing CLI interactive patterns in src/hlpr/cli/"
   Task: "Review current guided mode implementation for reuse opportunities"  
   Task: "Identify Rich display patterns for option collection UI"
   Task: "Document command template generation best practices"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: Enhance existing InteractiveSession class
   - Rationale: Maintains consistency with current architecture
   - Alternatives considered: New module vs enhancement approach

**Output**: research.md with implementation approach and pattern analysis

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - InteractiveSession (enhanced)
   - ProcessingOptions (new Pydantic model)
   - CommandTemplate (new data structure)
   - ProgressPhase (existing, document integration)

2. **Generate API contracts** from functional requirements:
   - Interactive method signatures for option collection
   - ProcessingOptions validation schemas
   - CommandTemplate generation interfaces
   - Progress tracking integration points

3. **Generate contract tests** from contracts:
   - test_cli_guided_enhanced.py (end-to-end guided workflow)
   - test_cli_interactive_options.py (option collection validation)
   - Tests validate FR-001 through FR-013 systematically

4. **Extract test scenarios** from user stories:
   - Default selection workflow (Enter key acceptance)
   - Advanced options configuration
   - Error handling and re-prompting
   - Graceful exit scenarios

5. **Update agent file incrementally**:
   - Run update-agent-context.sh for GitHub Copilot
   - Add guided workflow context and patterns
   - Document interactive CLI enhancement approach

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, .github/copilot-instructions.md

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from enhanced InteractiveSession design
- Contract test tasks for each functional requirement [P]
- Model creation for ProcessingOptions and CommandTemplate [P]
- Interactive method implementation tasks
- Integration tasks for existing CLI functions

**Ordering Strategy**:
- TDD order: Contract tests → Data models → Interactive methods → Integration
- Dependency order: Models → Validation → UI → Command generation
- Mark [P] for parallel execution where methods are independent

**Estimated Output**: 15-20 numbered, ordered tasks in tasks.md

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
| None | N/A | All requirements align with constitutional principles |

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*