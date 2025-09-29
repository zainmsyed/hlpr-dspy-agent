<!--
Sync Impact Report - Constitution Amendment v1.0.0 → v1.1.0
=============================================================
Version Change: v1.0.0 → v1.1.0 (MINOR - New principle added)
Date: 2025-09-28

ADDED SECTIONS:
- Principle VI: DRY (Don't Repeat Yourself) Code Practice - NEW principle enforcing code deduplication

TEMPLATES STATUS:
- ✅ .specify/templates/plan-template.md - Already aligned (references constitution checks)
- ✅ .specify/templates/spec-template.md - Already aligned (no code specifics)  
- ✅ .specify/templates/tasks-template.md - Already aligned (includes T022 Remove duplication task)

FOLLOW-UP TODOs: None - all templates already support the DRY principle
-->

# hlpr AI Assistant Constitution

## Core Principles

### I. Modular Architecture (NON-NEGOTIABLE)
Every feature must be implemented as a standalone, testable module with clear separation of concerns:
- **Core AI Logic** (DSPy/MIPRO) - Independent of CLI and API layers
- **File Processors** - Self-contained document/email parsing modules  
- **LLM Adapters** - Unified interface supporting both local and cloud models
- **CLI Interface** - Beautiful, interactive experience using Typer + Rich
- **API Layer** - FastAPI backend exposing core functionality
- Each module must be independently testable with clear interfaces

### II. Privacy-First Design (NON-NEGOTIABLE)
Local processing is the default; cloud services are opt-in:
- **Default Local LLM Support** - Primary focus on localhost endpoints (Ollama, etc.)
- **Secure Credential Storage** - Email credentials stored via system keyring
- **TLS/SSL Enforcement** - All network communications must be encrypted
- **Clear Data Flow** - Users must understand where their data goes
- **No Data Retention** - Process and return results without storing personal content

### III. CLI-First Experience
Every capability must be accessible via an intuitive, beautiful CLI:
- **Interactive Mode** - Step-by-step guided workflows for beginners
- **Power Mode** - Direct command execution for advanced users  
- **Rich Output** - Progress bars, syntax highlighting, tables, color coding
- **Error Handling** - Clear, actionable error messages with suggested fixes
- **Configuration Management** - Simple CLI commands for all settings

### IV. DSPy Integration & Optimization
All AI workflows must use DSPy with MIPRO optimization:
- **DSPy Signatures** - Define clear input/output contracts for AI tasks
- **MIPRO Optimization** - Automatically refine prompts for chosen LLM
- **Provider Flexibility** - Support local (HTTP API) and cloud LLMs seamlessly
- **Timeout Policies** - No timeouts for local providers by default; configurable for cloud
- **Error Recovery** - Retry mechanisms for transient failures

### V. Modern Tooling & Quality
Enforce modern Python development practices:
- **UV Dependency Management** - All dependencies managed via `uv add`
- **Ruff Code Quality** - Mandatory linting and formatting compliance
- **Type Hints** - Pydantic models for configuration and data validation
- **Structured Logging** - Clear, debuggable output for troubleshooting
- **Minimal Dependencies** - Keep core footprint small and focused

### VI. DRY (Don't Repeat Yourself) Code Practice (NON-NEGOTIABLE)
Eliminate code duplication systematically and proactively:
- **Zero Tolerance for Duplication** - Any code pattern repeated more than twice must be extracted
- **Shared Utilities** - Common functionality centralized in reusable modules
- **Configuration Consolidation** - Default values and settings managed in single locations
- **Template Abstraction** - Repetitive code patterns extracted into templates or base classes
- **Refactoring Priority** - Regular identification and elimination of duplicate code blocks
- **Measurement** - Track and reduce duplicate code metrics in each feature development cycle

## Technology Stack Requirements

### Required Dependencies
- **CLI & UX**: `typer`, `rich` - Interactive, beautiful command-line interface
- **AI Core**: `dspy`, `dspy-ai` - DSPy framework with MIPRO optimization  
- **LLM Integration**: `openai`, `anthropic`, `httpx` - Cloud and local model support
- **File Processing**: `PyPDF2`, `python-docx`, `markdown` - Document parsing
- **Email**: `aioimaplib`, `keyring` - Secure IMAP client with credential storage
- **API**: `fastapi`, `uvicorn` - REST API backend
- **Configuration**: `pydantic`, `pyyaml` - Type-safe settings management
- **Development**: `ruff` (linting/formatting), `pytest` (testing)

### Local LLM SupportS docume
- **Default Endpoint**: `http://localhost:11434` (Ollama)
- **Custom Endpoints**: User-configurable for llama.cpp, HuggingFace TGI, etc.
- **HTTP API Protocol**: Standard OpenAI-compatible endpoints preferred
- **No Timeout Policy**: Local providers default to no timeout to avoid interruptions

### Security Requirements
- **Credential Storage**: System keyring for email passwords/API keys
- **Network Security**: Enforce TLS/SSL for all external connections
- **API Security**: Basic API key protection for FastAPI endpoints
- **Data Handling**: No persistent storage of processed content

## Development Standards

### Code Quality (NON-NEGOTIABLE)
- **Ruff Compliance**: All code must pass `ruff check` and `ruff format`
- **Type Safety**: Pydantic models required for configuration and data structures
- **Error Handling**: Comprehensive exception handling with user-friendly messages
- **Documentation**: Docstrings required for public APIs and complex functions

### Testing Requirements  
- **Contract Tests**: All CLI commands and API endpoints
- **Integration Tests**: DSPy workflows, email processing, file parsing
- **Unit Tests**: Individual modules and functions
- **Test Organization**: `/tests/contract/`, `/tests/integration/`, `/tests/unit/`
- **Coverage**: Focus on critical paths and error scenarios

### Dependency Management
- **UV Only**: All package management via `uv add`, `uv remove`, `uv run`
- **Lock Files**: Maintain `uv.lock` for reproducible builds
- **Minimal Additions**: New dependencies require justification
- **Version Pinning**: Pin major versions for stability

## Governance

### Constitution Authority
This constitution supersedes all other development practices and decisions. All code changes, feature additions, and architectural decisions must comply with these principles.

### Amendment Process
- **Documentation Required**: All amendments must be documented with rationale
- **Testing Impact**: Changes affecting testing or quality standards require migration plan
- **Backward Compatibility**: Breaking changes to core principles require major version bump

### Development Workflow
- **Feature Development**: New features start as independent modules with tests
- **Code Review**: All PRs must verify compliance with constitution principles  
- **Quality Gates**: Ruff, type checking, and contract tests must pass before merge
- **Local Development**: Use project venv: `/home/zain/Documents/coding/hlpr/.venv/bin/python`

### Compliance Verification
- **Pre-commit**: Ruff formatting and linting on all commits
- **CI/CD**: Automated testing of contract, integration, and unit tests
- **Manual Review**: Architecture decisions reviewed against modular design principles
- **Performance**: Local LLM timeout policies and DSPy optimization effectiveness monitored

**Version**: 1.1.0 | **Ratified**: 2025-09-18 | **Last Amended**: 2025-09-28