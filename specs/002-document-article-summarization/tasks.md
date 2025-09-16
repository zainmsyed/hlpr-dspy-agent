# Tasks: Document & Article Summariz## 📊 **Current Status: Phase 3.4 COMPLETE** ✅

**Completed Tasks (T001-T017):**
- ✅ **Setup Phase (3.1)**: Document module structure, dependencies, linting
- ✅ **Tests Phase (3.2)**: Contract tests, integration tests (TDD approach)
- ✅ **Core Implementation (3.3)**: Document model, parser, summarizer, CLI, API
- ✅ **Integration Phase (3.4)**: DSPy integration, chunking, progress tracking, provider integration

**Key Achievements:**
- Document processing supports PDF, DOCX, TXT, MD formats
- CLI command `hlpr summarize document` with rich output
- API endpoint `POST /summarize/document` with file upload
- DSPy integration with fallback for reliability
- Comprehensive test coverage (5/5 document tests passing)
- Advanced chunking strategies (sentence, paragraph, fixed, token-based)
- Progress tracking with Rich UI and console fallbacks
- Multi-provider LLM support (local, OpenAI, Anthropic, Groq, Together AI)
- Security hardening: path validation, streaming processing, thread safety

**Next Phase: 3.5 Polish (IN PROGRESS)**
T018-T023: Unit tests, performance, documentation, quickstart, hallucination mitigation, verification
Design documents from `/home/zain/Documents/coding/hlpr/specs/002-document-article-summarization/`
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

## 📊 **Current Status: Phase 3.3 COMPLETE** ✅

**Completed Tasks (T001-T017):**
- ✅ **Setup Phase (3.1)**: Document module structure, dependencies, linting
- ✅ **Tests Phase (3.2)**: Contract tests, integration tests (TDD approach)
- ✅ **Core Implementation (3.3)**: Document model, parser, summarizer, CLI, API
- ✅ **Integration Phase (3.4)**: DSPy integration, chunking, progress tracking, provider integration

**Key Achievements:**
- Document processing supports PDF, DOCX, TXT, MD formats
- CLI command `hlpr summarize document` with rich output
- API endpoint `POST /summarize/document` with file upload
- DSPy integration with fallback for reliability
- Comprehensive test coverage (5/5 document tests passing)
- Security hardening: path validation, streaming processing, thread safety

**Next Phase: 3.4 Integration**
- T014-T017: DSPy integration, chunking, progress tracking, provider integration

**Remaining Tasks: T014-T021**
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
- [x] **T007** [P] Document entity model in src/hlpr/models/document.py
- [x] **T008** [P] Document parser library (PDF, DOCX, TXT, MD) in src/hlpr/document/parser.py
- [x] **T009** [P] Document summarization service in src/hlpr/document/summarizer.py
- [x] **T010** CLI summarize document command in src/hlpr/cli/summarize.py
- [x] **T011** API POST /summarize/document endpoint in src/hlpr/api/summarize.py
- [x] **T012** Input validation for document files
- [x] **T013** Error handling for document processing

## Phase 3.4: Integration
- [x] **T014** DSPy integration for document summarization in src/hlpr/llm/dspy_integration.py
- [x] **T015** Chunking strategy for large documents in src/hlpr/document/chunker.py
- [x] **T016** Progress tracking for document processing
- [x] **T017** LLM provider integration (local/cloud) for documents

## Phase 3.5: Polish (IN PROGRESS)
- [x] **T018** [P] Unit tests for document parsing in tests/unit/test_document_parser.py
- [x] **T019** Performance tests for document processing (<2s target)
- [x] **T020** [P] Document processing documentation in docs/document-processing.md (README updated with temperature docs)
- [x] **T021** Update quickstart guide with document examples (examples referenced in README)
- [x] **T022** Hallucination mitigation (basic detector + CLI warnings)
- [ ] **T023** Verification CLI & flow (opt-in hallucination verification via model)

## Phase 3.6: Code Quality & Refactoring (NEW - HIGH PRIORITY)
- [ ] **T024** Complete DSPy verify_claims refactor in src/hlpr/llm/dspy_integration.py
- [ ] **T025** [P] Split API endpoints: create /document/upload and /document/text in src/hlpr/api/summarize.py  
- [ ] **T026** [P] Centralized configuration management in src/hlpr/config.py
- [ ] **T027** [P] Custom exception hierarchy in src/hlpr/exceptions.py
- [ ] **T028** Enhanced structured logging across API and CLI modules

## Dependencies
- Tests (T004-T006) before implementation (T007-T013)
- T007 (Document model) blocks T008-T009 (parser/summarizer)
- T008-T009 blocks T010-T011 (CLI/API)
- T014 (DSPy) blocks T017 (provider integration)
- Implementation before polish (T018-T023)
- **Phase 3.6 Dependencies:**
  - T024 (DSPy refactor) should complete before other code quality tasks
  - T025-T028 can run in parallel (different files/modules)
  - T026 (config) blocks T027-T028 (exception/logging need config)

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
- [x] **Phase 3.3 Core Implementation: COMPLETE** ✅
- [x] **Critical Security Fixes Applied** ✅
- [x] **All Document Summarization Tests Passing** ✅

## 📋 **Detailed Task Descriptions - Phase 3.6**

### **T024: Complete DSPy verify_claims refactor** (CRITICAL)
**File**: `src/hlpr/llm/dspy_integration.py`
**Goal**: Remove C901 complexity warning without noqa suppression
**Actions**:
1. Extract `_verify_single_claim(source_text, claim) -> dict` method
2. Extract `_build_verification_result(claim, raw_result) -> dict` method  
3. Simplify main `verify_claims` to coordinate via list comprehension
4. Add unit tests mocking `dspy.Predict` for deterministic timeout/success scenarios
5. Verify Ruff passes without C901 noqa

### **T025: Split API endpoints** (HIGH)
**File**: `src/hlpr/api/summarize.py`
**Goal**: Reduce cognitive complexity by separating concerns
**Actions**:
1. Create `@router.post("/document/upload")` for file uploads only
2. Create `@router.post("/document/text")` for text content only
3. Keep existing `/document` endpoint for backward compatibility (delegate to new endpoints)
4. Move file validation logic to upload endpoint
5. Move text validation logic to text endpoint
6. Update OpenAPI documentation

### **T026: Centralized configuration management** (HIGH)
**File**: `src/hlpr/config.py` (new file)
**Goal**: Replace scattered constants with environment-driven config
**Actions**:
1. Create `@dataclass HlprConfig` with defaults:
   - `max_file_size: int = 100 * 1024 * 1024`
   - `max_text_length: int = 10 * 1024 * 1024`
   - `default_timeout: int = 30`
   - `allowed_origins: list[str]`
2. Add `@classmethod from_env(cls) -> HlprConfig` method
3. Replace constants in `summarize.py`, `main.py`
4. Update DSPy integration to use config timeouts
5. Add environment variable documentation

### **T027: Custom exception hierarchy** (MEDIUM)
**File**: `src/hlpr/exceptions.py` (new file)  
**Goal**: Replace generic exceptions with domain-specific error types
**Actions**:
1. Define base `HlprError(Exception)` class
2. Create `DocumentProcessingError(HlprError)` for parsing failures
3. Create `SummarizationError(HlprError)` for LLM failures
4. Create `ConfigurationError(HlprError)` for setup issues
5. Update error handling in API, CLI, and DSPy integration
6. Add structured error responses with error codes

### **T028: Enhanced structured logging** (MEDIUM)
**Files**: `src/hlpr/api/summarize.py`, `src/hlpr/cli/summarize.py`, `src/hlpr/llm/dspy_integration.py`
**Goal**: Improve observability with correlation IDs and metadata
**Actions**:
1. Add correlation ID generation (`str(uuid4())`) to request handlers
2. Replace `logger.exception()` calls with structured logging:
   ```python
   logger.info("Document processing started", extra={
       "correlation_id": correlation_id,
       "file_size": len(content), 
       "provider": provider_id,
       "processing_type": "file_upload"
   })
   ```
3. Add processing time, success/failure metrics
4. Include error context without sensitive data leakage
5. Update CLI to use structured logging for debugging modes