````markdown
# Tasks: hlpr — Personal AI Assistant

**Input**: Design documents from `/home/zain/Documents/coding/hlpr/specs/001-hlpr-ai-assistant/`
**Prerequisites**: plan.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

## Execution Flow (main)
```
1. Load plan.md from feature directory ✓
   → Tech stack: Python 3.11+, DSPy, FastAPI, Typer, Rich
   → Libraries: hlpr-document, hlpr-email, hlpr-llm, hlpr-cli, hlpr-api
   → Structure: Single project with modular libraries
2. Load design documents ✓:
   → data-model.md: 7 entities extracted → model tasks
   → contracts/: API spec + CLI spec → contract test tasks
   → research.md: Technical decisions → setup tasks
   → quickstart.md: User scenarios → integration tests
3. Generate tasks by category:
   → Setup: Python project, dependencies, tooling
   → Tests: contract tests, integration tests (TDD)
   → Core: models, libraries, CLI commands, API endpoints
   → Integration: DSPy, database, keyring, logging
   → Polish: unit tests, performance, documentation
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001-T041)
6. Dependencies: Setup → Tests → Models → Libraries → Integration → Polish
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
Single project structure per plan.md:
- **Source**: `src/hlpr/` (core library modules)
- **CLI**: `src/hlpr/cli/` (Typer commands)
- **API**: `src/hlpr/api/` (FastAPI endpoints)
- **Tests**: `tests/` (contract, integration, unit)

## Phase 3.1: Setup

- [ ] **T001** Create Python project structure with src/hlpr/, tests/, docs/ directories
- [ ] **T002** Initialize pyproject.toml with dependencies: dspy, fastapi, typer, rich, openai, anthropic, pypdf2, python-docx, aioimaplib, keyring, pydantic, httpx, pytest
- [ ] **T003** [P] Configure ruff for linting and formatting in pyproject.toml
- [ ] **T004** [P] Create .gitignore for Python project with common exclusions
- [ ] **T005** [P] Setup GitHub Actions workflow for CI/CD in .github/workflows/ci.yml

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests for API Endpoints
- [ ] **T006** [P] Contract test POST /summarize/document in tests/contract/test_summarize_document.py
- [ ] **T007** [P] Contract test POST /summarize/meeting in tests/contract/test_summarize_meeting.py
- [ ] **T008** [P] Contract test POST /email/process in tests/contract/test_email_process.py
- [ ] **T009** [P] Contract test GET /email/accounts in tests/contract/test_email_accounts_get.py
- [ ] **T010** [P] Contract test POST /email/accounts in tests/contract/test_email_accounts_post.py
- [ ] **T011** [P] Contract test GET /providers in tests/contract/test_providers.py
- [ ] **T012** [P] Contract test GET /jobs/{job_id} in tests/contract/test_jobs.py

### Contract Tests for CLI Commands
- [ ] **T013** [P] Contract test hlpr summarize document command in tests/contract/test_cli_summarize_document.py
- [ ] **T014** [P] Contract test hlpr summarize meeting command in tests/contract/test_cli_summarize_meeting.py
- [ ] **T015** [P] Contract test hlpr email process command in tests/contract/test_cli_email_process.py
- [ ] **T016** [P] Contract test hlpr email accounts commands in tests/contract/test_cli_email_accounts.py
- [ ] **T017** [P] Contract test hlpr config commands in tests/contract/test_cli_config.py
- [ ] **T018** [P] Contract test hlpr providers commands in tests/contract/test_cli_providers.py

### Integration Tests from Quickstart Scenarios
- [ ] **T019** [P] Integration test document summarization workflow in tests/integration/test_document_workflow.py
- [ ] **T020** [P] Integration test meeting processing workflow in tests/integration/test_meeting_workflow.py
- [ ] **T021** [P] Integration test email processing workflow in tests/integration/test_email_workflow.py
- [ ] **T022** [P] Integration test provider management workflow in tests/integration/test_provider_workflow.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Data Models
- [ ] **T023** [P] Document entity model in src/hlpr/models/document.py
- [ ] **T024** [P] MeetingNote and ActionItem models in src/hlpr/models/meeting.py
- [ ] **T025** [P] EmailAccount and EmailMessage models in src/hlpr/models/email.py
- [ ] **T026** [P] AIProvider model in src/hlpr/models/provider.py
- [ ] **T027** [P] ProcessingJob model in src/hlpr/models/job.py
- [ ] **T028** [P] Database schema and SQLite setup in src/hlpr/db/schema.py

### Core Libraries
- [ ] **T029** [P] Document parser library (PDF, DOCX, TXT, MD) in src/hlpr/document/parser.py
- [ ] **T030** [P] Document summarization service in src/hlpr/document/summarizer.py
- [ ] **T031** [P] Email IMAP client in src/hlpr/email/client.py
- [ ] **T032** [P] Email classification service in src/hlpr/email/classifier.py
- [ ] **T033** [P] LLM provider adapter (local/cloud) in src/hlpr/llm/adapter.py
- [ ] **T034** [P] DSPy integration and MIPRO optimizer in src/hlpr/llm/dspy_integration.py

### CLI Implementation
- [ ] **T035** CLI main entry point and Typer app in src/hlpr/cli/main.py
- [ ] **T036** CLI summarize commands in src/hlpr/cli/summarize.py
- [ ] **T037** CLI email commands in src/hlpr/cli/email.py
- [ ] **T038** CLI config commands in src/hlpr/cli/config.py
- [ ] **T039** CLI provider commands in src/hlpr/cli/providers.py

### API Implementation
- [ ] **T040** FastAPI app setup and middleware in src/hlpr/api/main.py
- [ ] **T041** API summarization endpoints in src/hlpr/api/summarize.py
- [ ] **T042** API email endpoints in src/hlpr/api/email.py
- [ ] **T043** API provider endpoints in src/hlpr/api/providers.py

## Phase 3.4: Integration

- [ ] **T044** Configuration management with YAML and keyring in src/hlpr/config/manager.py
- [ ] **T045** Rich terminal formatting and progress bars in src/hlpr/cli/formatting.py
- [ ] **T046** Logging setup with structured output in src/hlpr/utils/logging.py
- [ ] **T047** Error handling and custom exceptions in src/hlpr/utils/exceptions.py
- [ ] **T048** Chunking strategy for large documents in src/hlpr/document/chunker.py
- [ ] **T049** Background job processing system in src/hlpr/jobs/processor.py

## Phase 3.5: Polish

- [ ] **T050** [P] Unit tests for document parsing in tests/unit/test_document_parser.py
- [ ] **T051** [P] Unit tests for email classification in tests/unit/test_email_classifier.py
- [ ] **T052** [P] Unit tests for LLM adapter in tests/unit/test_llm_adapter.py
- [ ] **T053** [P] Unit tests for configuration management in tests/unit/test_config.py
- [ ] **T054** Performance tests for large document processing in tests/performance/test_large_documents.py
- [ ] **T055** [P] CLI documentation in docs/cli-reference.md
- [ ] **T056** [P] API documentation in docs/api-reference.md
- [ ] **T057** [P] Installation and setup guide in docs/installation.md
- [ ] **T058** Package configuration for pip installation in setup.py and MANIFEST.in
- [ ] **T059** Validate quickstart guide scenarios manually

## Dependencies

**Critical TDD Dependencies**:
- All tests (T006-T022) MUST complete before ANY implementation (T023+)
- Tests must fail initially to ensure TDD compliance

**Implementation Dependencies**:
- T028 (database schema) blocks T044 (config manager)
- T023-T027 (models) block T029-T034 (libraries)
- T029-T034 (libraries) block T035-T043 (CLI/API)
- T044-T049 (integration) required for T050+ (polish)

**Parallel Execution Safe**:
- Contract tests (T006-T018) can run in parallel
- Integration tests (T019-T022) can run in parallel  
- Model creation (T023-T027) can run in parallel
- Core libraries (T029-T034) can run in parallel
- Unit tests (T050-T053) can run in parallel
- Documentation (T055-T057) can run in parallel

## Parallel Execution Examples

### Phase 3.2: All Contract Tests Together
```bash
# Launch T006-T018 simultaneously:
Task: "Contract test POST /summarize/document in tests/contract/test_summarize_document.py"
Task: "Contract test POST /summarize/meeting in tests/contract/test_summarize_meeting.py"
Task: "Contract test POST /email/process in tests/contract/test_email_process.py"
Task: "Contract test GET /email/accounts in tests/contract/test_email_accounts_get.py"
Task: "Contract test POST /email/accounts in tests/contract/test_email_accounts_post.py"
Task: "Contract test GET /providers in tests/contract/test_providers.py"
Task: "Contract test GET /jobs/{job_id} in tests/contract/test_jobs.py"
Task: "Contract test hlpr summarize document in tests/contract/test_cli_summarize_document.py"
Task: "Contract test hlpr summarize meeting in tests/contract/test_cli_summarize_meeting.py"
Task: "Contract test hlpr email process in tests/contract/test_cli_email_process.py"
Task: "Contract test hlpr email accounts in tests/contract/test_cli_email_accounts.py"
Task: "Contract test hlpr config commands in tests/contract/test_cli_config.py"
Task: "Contract test hlpr providers commands in tests/contract/test_cli_providers.py"
```

### Phase 3.3: Model Creation in Parallel
```bash
# Launch T023-T027 simultaneously:
Task: "Document entity model in src/hlpr/models/document.py"
Task: "MeetingNote and ActionItem models in src/hlpr/models/meeting.py"
Task: "EmailAccount and EmailMessage models in src/hlpr/models/email.py"
Task: "AIProvider model in src/hlpr/models/provider.py"
Task: "ProcessingJob model in src/hlpr/models/job.py"
```

### Phase 3.3: Core Libraries in Parallel  
```bash
# Launch T029-T034 simultaneously:
Task: "Document parser library in src/hlpr/document/parser.py"
Task: "Document summarization service in src/hlpr/document/summarizer.py"
Task: "Email IMAP client in src/hlpr/email/client.py"
Task: "Email classification service in src/hlpr/email/classifier.py"
Task: "LLM provider adapter in src/hlpr/llm/adapter.py"
Task: "DSPy integration and MIPRO optimizer in src/hlpr/llm/dspy_integration.py"
```

## Task Generation Rules Applied

**From API Contracts (api-spec.yaml)**:
- 7 endpoints → 7 contract test tasks (T006-T012)
- 7 endpoints → implementation in API modules (T041-T043)

**From CLI Contracts (cli-spec.md)**:
- 6 command groups → 6 contract test tasks (T013-T018)
- 6 command groups → implementation in CLI modules (T035-T039)

**From Data Model (data-model.md)**:
- 7 entities → 6 model creation tasks (T023-T027, T028 for schema)
- Relationships → service layer in libraries (T029-T034)

**From Quickstart Scenarios**:
- 4 main workflows → 4 integration tests (T019-T022)
- Manual validation → T059

**From Research & Plan**:
- Technical decisions → setup tasks (T001-T005)
- Integration requirements → T044-T049
- Performance needs → T054

## Validation Checklist

- [x] All API contracts have corresponding tests (T006-T012)
- [x] All CLI contracts have corresponding tests (T013-T018)
- [x] All entities have model tasks (T023-T027)
- [x] All tests come before implementation (Phase 3.2 before 3.3)
- [x] Parallel tasks are truly independent (different files)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] TDD ordering enforced (tests must fail before implementation)
- [x] Quickstart scenarios covered by integration tests
- [x] Constitutional principles followed (library-first, CLI per library)

## Notes

- **TDD Enforcement**: All contract and integration tests (T006-T022) must be completed and failing before starting any implementation (T023+)
- **Parallel Safety**: Tasks marked [P] operate on different files and have no dependencies
- **File Organization**: Follows single project structure with modular library organization
- **Constitutional Compliance**: Every feature implemented as a library with CLI interface
- **Commit Strategy**: Commit after each task completion for incremental progress
- **Error Handling**: Each implementation task includes proper error handling and logging
- **Testing Strategy**: Contract → Integration → Unit test coverage at each level
````