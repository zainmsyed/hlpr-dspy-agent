
# Implementation Plan: Update Config Workflow

**Branch**: `007-update-config-workflow` | **Date**: September 30, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-update-config-workflow/spec.md`

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
Implement a unified configuration management system that allows users to set up their preferences once (AI provider, output format, API keys) and have them remembered across sessions. The system will provide both guided workflow setup and direct file editing capabilities, with secure API key storage and graceful error handling.

## Technical Context
**Language/Version**: Python 3.11+  
**Primary Dependencies**: Typer, Rich, Pydantic, PyYAML (to be added)  
**Storage**: YAML config files + .env files in ~/.hlpr/ directory  
**Testing**: pytest with contract/integration/unit test structure  
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows)  
**Project Type**: Single project - extends existing hlpr CLI application  
**Performance Goals**: <100ms config loading/saving for imperceptible UX  
**Constraints**: File permissions (chmod 600), graceful fallback for corrupted configs  
**Scale/Scope**: Single-user personal productivity tool with <1MB config files

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**I. Modular Architecture**: ✅ PASS - Configuration management will be implemented as a standalone module (src/hlpr/config/) with clear interfaces

**II. Privacy-First Design**: ✅ PASS - API keys stored securely with chmod 600, no cloud storage, local file-based configuration

**III. CLI-First Experience**: ✅ PASS - All functionality accessible via hlpr config commands with Rich interactive prompts

**IV. DSPy Integration**: ✅ PASS - No AI workflows in config management, existing DSPy integration unchanged

**V. Modern Tooling**: ✅ PASS - Uses Pydantic for validation, Typer for CLI, follows existing project patterns

**VI. DRY Code Practice**: ✅ PASS - Consolidates scattered configuration into single module, eliminates duplication

**Constitutional Compliance**: All principles satisfied. No violations requiring justification.

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
├── config/
│   ├── __init__.py          # Configuration management module exports
│   ├── manager.py           # ConfigurationManager class - load/save operations
│   ├── models.py            # Pydantic models for config structure validation
│   ├── defaults.py          # Default configuration values and constants
│   ├── validators.py        # Configuration validation logic
│   └── migration.py         # Migration from existing config formats
├── cli/
│   └── config_commands.py   # Enhanced hlpr config CLI commands (setup, show, edit, reset)
└── [existing modules unchanged]

tests/
├── contract/
│   └── test_config_commands.py  # Contract tests for CLI config commands
├── integration/
│   └── test_config_integration.py  # End-to-end config workflow tests
└── unit/
    └── test_config_manager.py   # Unit tests for config manager and models
```

**Structure Decision**: Single project extension - adds new config management module to existing hlpr CLI application structure, maintaining modular architecture.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   ✅ Configuration file format selection (YAML + .env)
   ✅ File location strategy (~/.hlpr/ directory)
   ✅ Performance optimization approach (caching with modification checking)
   ✅ Security implementation (chmod 600 for .env files)

2. **Generate and dispatch research agents**:
   ✅ Configuration management best practices researched
   ✅ Error handling patterns for file-based config identified
   ✅ Cross-platform compatibility considerations documented

3. **Consolidate findings** in `research.md`:
   ✅ All technical decisions documented with rationale
   ✅ Risk assessment completed
   ✅ Implementation patterns identified

**Output**: ✅ research.md complete with all technical decisions resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete* ✅

1. **Extract entities from feature spec** → `data-model.md`:
   ✅ UserConfiguration, APICredentials, ConfigurationState models defined
   ✅ Validation rules and constraints documented
   ✅ File structure and path management specified

2. **Generate API contracts** from functional requirements:
   ✅ ConfigurationManagerInterface with complete method contracts
   ✅ CLI command specifications with options and error handling
   ✅ Integration contracts for existing systems

3. **Generate contract tests** from contracts:
   ✅ Test scenarios defined for all user stories
   ✅ Performance validation procedures specified
   ✅ Error recovery scenarios documented

4. **Extract test scenarios** from user stories:
   ✅ 6 comprehensive user scenarios for validation
   ✅ Edge case testing procedures defined
   ✅ Integration testing approach documented

5. **Update agent file incrementally**:
   ✅ GitHub Copilot instructions updated with configuration context
   ✅ Technical stack additions documented
   ✅ Development patterns preserved

**Output**: ✅ data-model.md, /contracts/* specifications, quickstart.md validation procedures, updated .github/copilot-instructions.md

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load data-model.md and contracts/ specifications as input
- Generate implementation tasks following TDD approach
- Create tasks for ConfigurationManager class and CLI commands
- Include migration and validation components
- Ensure PyYAML dependency addition

**Specific Task Categories**:
1. **Foundation Tasks** [P] - Parallel execution
   - Add PyYAML dependency via `uv add`
   - Create configuration models (UserConfiguration, APICredentials, etc.)
   - Implement ConfigurationPaths utility class

2. **Core Logic Tasks** - Sequential dependencies
   - Implement ConfigurationManager with file operations
   - Add validation logic and error handling
   - Create migration utilities for existing configs

3. **CLI Integration Tasks** [P] - Parallel execution
   - Implement `hlpr config setup` command with Rich prompts
   - Implement `hlpr config show/edit/reset/validate` commands
   - Update existing commands to load configuration

4. **Testing Tasks** [P] - Parallel execution
   - Contract tests for all CLI commands
   - Integration tests for configuration workflows
   - Unit tests for ConfigurationManager and models

**Ordering Strategy**:
- Dependencies before dependents (models → manager → CLI)
- Tests in parallel with implementation tasks
- Contract tests first to define expected behavior
- Integration tests to validate complete workflows

**Estimated Output**: 20-25 numbered, prioritized tasks with clear dependencies and parallel execution markers

**Key Dependencies Identified**:
- PyYAML package addition must complete before file operations
- Data models must exist before ConfigurationManager implementation
- ConfigurationManager must exist before CLI command implementation
- Migration logic requires existing configuration analysis

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
- [x] Phase 0: Research complete (/plan command) ✅
- [x] Phase 1: Design complete (/plan command) ✅
- [ ] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS ✅
- [x] Post-Design Constitution Check: PASS ✅
- [x] All NEEDS CLARIFICATION resolved ✅
- [x] Complexity deviations documented: N/A (no violations) ✅

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
