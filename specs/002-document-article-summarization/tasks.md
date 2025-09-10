# Tasks: Document & Article Summarization

**Input**: Design documents from `/home/zain/Documents/coding/hlpr/specs/002-document-article-summarization/`
**Prerequisites**: plan.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

## Execution Flow (main)
```
1. Load plan.md from feature directory ✓
   → Tech stack: Python 3.11+, DSPy, PyPDF2, python-docx, httpx
   → Libraries: hlpr-document (parser, summarizer)
   → Structure: Single project with modular libraries
2. Load design documents ✓:
   → data-model.md: Document entity → model tasks
   → contracts/: api-spec.yaml, cli-spec.md → contract test tasks
   → research.md: DSPy, parsing, chunking decisions → setup tasks
   → quickstart.md: Document scenarios → integration tests
3. Generate tasks by category:
   → Setup: Document module structure, dependencies
   → Tests: Contract tests, integration tests (TDD)
   → Core: Document model, parser, summarizer, CLI, API
   → Integration: DSPy, chunking, providers
   → Polish: Unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001-T021)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests? ✓
   → All entities have models? ✓
   → All endpoints implemented? ✓
9. Return: SUCCESS (tasks ready for execution)
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
- [x] **T001** Create document processing module structure in src/hlpr/document/
- [x] **T002** Add document processing dependencies (PyPDF2, python-docx) to pyproject.toml
- [x] **T003** [P] Configure document-specific linting rules in pyproject.toml

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [x] **T004** [P] Contract test POST /summarize/document in tests/contract/test_api_summarize_document.py
- [x] **T005** [P] Contract test hlpr summarize document in tests/contract/test_cli_summarize_document.py
- [x] **T006** [P] Integration test document summarization workflow in tests/integration/test_document_workflow.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [ ] **T007** [P] Document entity model in src/hlpr/models/document.py
- [ ] **T008** [P] Document parser library (PDF, DOCX, TXT, MD) in src/hlpr/document/parser.py
- [ ] **T009** [P] Document summarization service in src/hlpr/document/summarizer.py
- [ ] **T010** CLI summarize document command in src/hlpr/cli/summarize.py
- [ ] **T011** API POST /summarize/document endpoint in src/hlpr/api/summarize.py
- [ ] **T012** Input validation for document files
- [ ] **T013** Error handling for document processing

## Phase 3.4: Integration
- [ ] **T014** DSPy integration for document summarization in src/hlpr/llm/dspy_integration.py
- [ ] **T015** Chunking strategy for large documents in src/hlpr/document/chunker.py
- [ ] **T016** Progress tracking for document processing
- [ ] **T017** LLM provider integration (local/cloud) for documents

## Phase 3.5: Polish
- [ ] **T018** [P] Unit tests for document parsing in tests/unit/test_document_parser.py
- [ ] **T019** Performance tests for document processing (<2s target)
- [ ] **T020** [P] Document processing documentation in docs/document-processing.md
- [ ] **T021** Update quickstart guide with document examples

## Dependencies
- Tests (T004-T006) before implementation (T007-T013)
- T007 (Document model) blocks T008-T009 (parser/summarizer)
- T008-T009 blocks T010-T011 (CLI/API)
- T014 (DSPy) blocks T017 (provider integration)
- Implementation before polish (T018-T021)

## Parallel Execution Examples
```
# Document Tests Together:
Task: "Contract test POST /summarize/document in tests/contract/test_api_summarize_document.py"
Task: "Contract test hlpr summarize document in tests/contract/test_cli_summarize_document.py"
Task: "Integration test document summarization workflow in tests/integration/test_document_workflow.py"

# Core Implementation in Parallel:
Task: "Document entity model in src/hlpr/models/document.py"
Task: "Document parser library in src/hlpr/document/parser.py"
Task: "Document summarization service in src/hlpr/document/summarizer.py"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Focus on document summarization feature
- Avoid: vague tasks, same file conflicts

## Task Generation Rules Applied
1. **From Contracts**:
   - api-spec.yaml → T004 contract test [P]
   - cli-spec.md → T005 contract test [P]
   - POST /summarize/document → T011 implementation
   - hlpr summarize document → T010 implementation

2. **From Data Model**:
   - Document entity → T007 model creation [P]

3. **From User Stories**:
   - Document summarization scenarios → T006 integration test [P]

4. **Ordering**:
   - Setup → Tests → Models → Services → CLI/API → Integration → Polish
   - Dependencies block parallel execution

## Validation Checklist
- [x] All contracts have corresponding tests (T004-T005)
- [x] All entities have model tasks (T007)
- [x] All tests come before implementation (Phase 3.2 before 3.3)
- [x] Parallel tasks are truly independent (different files)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task