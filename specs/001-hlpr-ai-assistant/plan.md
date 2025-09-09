# Implementation Plan: hlpr — Personal AI Assistant

**Branch**: `001-hlpr-ai-assistant` | **Date**: 2025-09-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/home/zain/Documents/coding/hlpr/specs/001-hlpr-ai-assistant/spec.md`

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
Personal AI assistant (hlpr) that provides local-first document summarization, meeting note processing, and email classification. Modular CLI application with optional FastAPI backend, supporting both local LLMs (Ollama) and cloud providers (OpenAI, Anthropic). Built with DSPy/MIPRO for optimized AI workflows, Typer/Rich for beautiful CLI experience, and secure credential storage via system keyring.

## Technical Context
**Language/Version**: Python 3.11+  
**Primary Dependencies**: DSPy, MIPRO, FastAPI, Typer, Rich, OpenAI, Anthropic, PyPDF2, python-docx, aioimaplib, keyring, pydantic, httpx  
**Storage**: File-based (documents, meeting notes), system keyring (credentials), optional local file caching  
**Testing**: pytest, contract tests, integration tests with real LLM endpoints  
**Target Platform**: Linux, macOS, Windows (cross-platform CLI)  
**Project Type**: single (CLI + optional API backend)  
**Performance Goals**: <2s document parsing, <5s LLM response for 10k tokens, efficient chunking for large files  
**Constraints**: Privacy-first (local processing preferred), minimal dependencies, graceful degradation, secure credential storage  
**Scale/Scope**: Personal use tool, 10-1000 documents, 100-10k emails, 1-10 configured accounts

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**:
- Projects: 2 (hlpr-cli, hlpr-api) - CLI as primary, API as optional backend
- Using framework directly? Yes - FastAPI, Typer, DSPy used directly without wrappers
- Single data model? Yes - unified entities (Document, EmailMessage, etc.) across CLI/API
- Avoiding patterns? Yes - direct service classes, no Repository/UoW patterns

**Architecture**:
- EVERY feature as library? Yes - document processor, email client, LLM adapter as libraries
- Libraries listed: 
  - hlpr-document: PDF/DOCX/TXT/MD parsing and summarization
  - hlpr-email: IMAP client, classification, summarization  
  - hlpr-llm: LLM adapter (local/cloud), DSPy integration
  - hlpr-cli: CLI interface using Typer/Rich
  - hlpr-api: FastAPI backend (optional)
- CLI per library: hlpr summarize, hlpr email, hlpr config with --help/--version/--format
- Library docs: llms.txt format planned for each library

**Testing (NON-NEGOTIABLE)**:
- RED-GREEN-Refactor cycle enforced? Yes - tests written first, must fail before implementation
- Git commits show tests before implementation? Yes - contract tests committed before code
- Order: Contract→Integration→E2E→Unit strictly followed? Yes
- Real dependencies used? Yes - actual LLM endpoints, real IMAP servers for integration tests
- Integration tests for: new libraries (document, email, llm), contract changes, shared data models
- FORBIDDEN: Implementation before test, skipping RED phase

**Observability**:
- Structured logging included? Yes - using Python logging with JSON output
- Frontend logs → backend? N/A (CLI-first, API optional)
- Error context sufficient? Yes - Rich formatting for CLI errors, structured API responses

**Versioning**:
- Version number assigned? 0.1.0 (initial implementation)
- BUILD increments on every change? Yes - following semantic versioning
- Breaking changes handled? Yes - parallel tests during API changes

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

**Structure Decision**: Option 1 (Single project) - CLI-first application with optional API backend, not a web/mobile app

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
- Load `/templates/tasks-template.md` as base template
- Generate tasks from Phase 1 design artifacts:
  - Each API endpoint in `contracts/api-spec.yaml` → contract test task [P]
  - Each CLI command in `contracts/cli-spec.md` → contract test task [P]
  - Each entity in `data-model.md` → model implementation task [P]
  - Each quickstart scenario → integration test task
  - Each library (document, email, llm, cli, api) → implementation tasks

**Task Categories & Dependencies**:
1. **Infrastructure Setup** [P]: Project structure, dependencies, configuration
2. **Data Models** [P]: SQLite schema, Pydantic models, entity classes
3. **Contract Tests**: API endpoints tests, CLI command tests (must fail initially)
4. **Core Libraries**:
   - hlpr-llm: DSPy integration, provider adapters [P]
   - hlpr-document: File parsers, text extraction [P] 
   - hlpr-email: IMAP client, message processing [P]
5. **CLI Implementation**: Typer commands, Rich formatting, configuration management
6. **API Implementation**: FastAPI endpoints, request/response handling
7. **Integration Tests**: End-to-end scenarios from quickstart.md
8. **Deployment**: Packaging, installation, documentation

**Ordering Strategy**:
- TDD order: All contract tests before any implementation
- Dependency order: Models → Libraries → CLI → API → Integration
- Parallel execution: Mark independent tasks with [P] for concurrent development
- Constitution compliance: Every feature as library, no implementation before tests

**Estimated Output**: 35-40 numbered tasks in dependency order:
- 5 infrastructure/setup tasks
- 8 model and contract test tasks  
- 15 library implementation tasks (3 per library)
- 8 CLI/API implementation tasks
- 6 integration and deployment tasks

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
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS  
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*