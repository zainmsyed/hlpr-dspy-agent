# hlpr Codebase Guide for Junior Developers

This document explains the structure and purpose of each file in the hlpr codebase to help new developers understand how everything fits together.

## 📁 Project Overview

hlpr is a document summarization tool with both CLI and API interfaces. It uses AI providers (local, OpenAI, Anthropic, etc.) to generate summaries of documents in various formats (PDF, DOCX, TXT, MD).

## 🏗️ Project Structure

```
hlpr/
├── src/hlpr/               # Main application code
├── tests/                  # All test files
├── docs/                   # Documentation
├── documents/              # Example documents and specs
├── specs/                  # Feature specifications
└── pyproject.toml          # Python project configuration
```

---

## 📦 src/hlpr/ - Main Application Code

### Core Entry Points
- **`__init__.py`** - Package initialization, exports main classes
- **`__about__.py`** - Version information and package metadata

### 🌐 API Layer (`src/hlpr/api/`)
The FastAPI web server that provides HTTP endpoints.

- **`main.py`** - FastAPI app setup, middleware, CORS configuration
- **`summarize.py`** - Document summarization endpoints (`/summarize/document`, `/summarize/meeting`)
- **`email.py`** - Email processing endpoints (if enabled)
- **`jobs.py`** - Background job management endpoints
- **`utils.py`** - API utility functions (serialization, validation)

### 🖥️ CLI Layer (`src/hlpr/cli/`)
The command-line interface using Typer for terminal interaction.

#### Main CLI Files
- **`main.py`** - Main CLI app setup, global commands, help system
- **`summarize.py`** - Document summarization commands (`hlpr summarize document`, `hlpr summarize meeting`)
- **`email.py`** - Email processing CLI commands
- **`config.py`** - Configuration management commands (`hlpr config`)

#### CLI Support Files
- **`batch.py`** - Batch processing multiple files at once
- **`interactive.py`** - Interactive/guided mode workflows
- **`console.py`** - Console output adapter (backward compatibility)
- **`output.py`** - CLI output formatting and Rich Console fallbacks
- **`rich_display.py`** - Rich terminal UI components (progress bars, panels)
- **`renderers.py`** - Output format renderers (JSON, Markdown, plain text)
- **`validators.py`** - Input validation for CLI arguments
- **`prompt_providers.py`** - Interactive prompts and user input
- **`providers.py`** - AI provider selection and configuration
- **`template_commands.py`** - Saved command template management
- **`help_display.py`** - Custom help text formatting
- **`models.py`** - CLI-specific data models
- **`prompts.py`** - User prompt text and templates
- **`option_collectors.py`** - CLI option parsing and collection

### ⚙️ Configuration (`src/hlpr/config/`)
Application configuration and settings management.

- **`__init__.py`** - Config package exports and legacy compatibility
- **`facade.py`** - ConfigFacade class for centralized config access
- **`loader.py`** - Configuration file loading and parsing
- **`migration.py`** - Config schema migration system
- **`platform.py`** - Platform-specific defaults and settings
- **`recovery.py`** - Configuration error recovery
- **`validators.py`** - Configuration validation rules
- **`guided.py`** - Guided mode configuration helpers
- **`ui_strings.py`** - User interface text and messages
- **`_atomic.py`** - Atomic file operations for config safety

### 📄 Document Processing (`src/hlpr/document/`)
Document parsing, processing, and summarization logic.

- **`parser/`**
  - **`__init__.py`** - Main DocumentParser class, handles PDF/DOCX/TXT/MD files
- **`summarizer/`**
  - **`__init__.py`** - DocumentSummarizer class, orchestrates AI summarization
- **`chunker.py`** - Splits large documents into manageable chunks
- **`progress.py`** - Progress tracking for long-running operations

### 🧠 LLM Integration (`src/hlpr/llm/`)
Integration with Large Language Models and AI providers.

- **`dspy_integration.py`** - DSPy framework integration for prompt optimization

### 🗃️ Data Models (`src/hlpr/models/`)
Pydantic models for data validation and serialization.

- **`document.py`** - Document model (file metadata, processing state)
- **`interactive.py`** - Interactive session models
- **`saved_commands.py`** - Saved command template models
- **`templates.py`** - Command template data structures
- **`user_preferences.py`** - User preference models

### 🛠️ Utilities (`src/hlpr/utils/`)
Shared utility functions and helpers.

- **`__init__.py`** - Utility package exports
- **`file_validation.py`** - File existence and readability validation
- **`error_handling.py`** - Error handling utilities
- **`validation_messages.py`** - Validation message data structures
- **`config_helpers.py`** - Configuration access helpers

### ⚠️ Exceptions (`src/hlpr/exceptions/`)
Custom exception classes for better error handling.

- **`__init__.py`** - Main exception classes (HlprError, DocumentProcessingError, etc.)
- **`guided.py`** - Guided mode specific exceptions

### 📁 I/O Operations (`src/hlpr/io/`)
Input/output operations and file handling.

- **`atomic.py`** - Atomic file operations

### 📊 Logging (`src/hlpr/`)
Logging and monitoring utilities.

- **`logging_utils.py`** - Structured logging, correlation IDs
- **`deprecations.py`** - Deprecation warning helpers

### ⚙️ Core Configuration Files
- **`config.py`** - Main configuration class and settings
- **`config_helpers.py`** - Configuration access helpers
- **`exceptions.py`** - Core exception definitions

---

## 🧪 tests/ - Test Suite

### Test Organization
- **`contract/`** - Contract tests (API behavior validation)
- **`integration/`** - Integration tests (full workflow testing)
- **`unit/`** - Unit tests (individual function/class testing)
- **`performance/`** - Performance benchmarks and regression tests

### Key Test Files
- **`conftest.py`** - Pytest configuration and shared fixtures
- **`README.md`** - Testing documentation and guidelines

---

## 📖 Documentation Files

### Root Level Documentation
- **`README.md`** - Main project documentation and quick start
- **`MIGRATION.md`** - Configuration migration guide
- **`pytest.ini`** - Pytest configuration
- **`pyproject.toml`** - Python project metadata, dependencies, and build config

### 📋 specs/ - Feature Specifications
Detailed specifications for major features, organized by feature number:
- **`001-hlpr-ai-assistant/`** - AI assistant core functionality
- **`002-document-article-summarization/`** - Document summarization features
- **`003-cli-tui-of/`** - CLI and TUI enhancements
- **`004-guided-mode/`** - Interactive guided workflows
- **`005-core-configuration-and-ui-management/`** - Configuration system

Each spec directory contains:
- **`spec.md`** - Feature requirements and acceptance criteria
- **`plan.md`** - Implementation plan and architecture
- **`tasks.md`** - Detailed task breakdown
- **`data-model.md`** - Data structures and models
- **`quickstart.md`** - Quick implementation guide
- **`research.md`** - Research notes and decisions
- **`contracts/`** - API contracts and interfaces

### 📄 documents/ - Examples and References
- **`examples/`** - Sample documents for testing (cover_letter.md, etc.)
- **`future_features_modularization.md`** - Planned feature roadmap
- **`hlpr-prd.md`** - Product requirements document

---

## 🔄 Data Flow

### CLI Flow
1. **CLI Entry** (`cli/main.py`) → Parse commands
2. **Document Processing** (`document/parser/`) → Extract text
3. **Summarization** (`document/summarizer/`) → Generate summary via LLM
4. **Output** (`cli/renderers.py`) → Format and display results

### API Flow
1. **HTTP Request** (`api/main.py`) → Route to endpoint
2. **Document Upload** (`api/summarize.py`) → Validate and process
3. **Document Processing** → Same as CLI flow
4. **JSON Response** → Return structured results

### Configuration Flow
1. **Config Loading** (`config/loader.py`) → Load from files/environment
2. **Migration** (`config/migration.py`) → Update old config formats
3. **Validation** (`config/validators.py`) → Ensure valid settings
4. **Access** (`config/facade.py`) → Centralized config access

---

## 🎯 Key Design Patterns

### 1. **Facade Pattern**
- `ConfigFacade` centralizes configuration access
- `DocumentSummarizer` orchestrates the summarization pipeline

### 2. **Strategy Pattern**
- Multiple AI providers (local, OpenAI, Anthropic) with common interface
- Different output renderers (JSON, Markdown, Rich) with common interface

### 3. **Command Pattern**
- CLI commands are organized as separate modules
- Saved command templates for reusable operations

### 4. **Factory Pattern**
- Provider creation based on configuration
- Progress tracker creation based on context

---

## 🚀 Getting Started as a Junior Developer

### 1. **Start Here**
- Read `README.md` for project overview
- Run the CLI: `hlpr summarize document documents/examples/cover_letter.md`
- Explore the API: Start with `api/main.py` and `api/summarize.py`

### 2. **Common Tasks**
- **Adding a new CLI command**: Create in `cli/` and register in `cli/main.py`
- **Adding a new API endpoint**: Add to appropriate file in `api/`
- **Adding a new document format**: Extend `document/parser/__init__.py`
- **Adding configuration options**: Update `config.py` and add migration if needed

### 3. **Testing**
- Unit tests: Test individual functions in isolation
- Integration tests: Test full workflows end-to-end
- Contract tests: Test API behavior and interfaces

### 4. **Key Files to Understand First**
1. `src/hlpr/cli/main.py` - CLI entry point
2. `src/hlpr/api/main.py` - API entry point
3. `src/hlpr/document/parser/__init__.py` - Document processing
4. `src/hlpr/document/summarizer/__init__.py` - Summarization logic
5. `src/hlpr/config.py` - Configuration system

---

## ❓ Questions?

If you're a junior developer working on this codebase and have questions:

1. **Check the tests** - They often show how components are meant to be used
2. **Look at similar code** - Find existing patterns to follow
3. **Check the specs** - Feature specifications explain the "why" behind the code
4. **Run the code locally** - Get hands-on experience with the functionality

Happy coding! 🎉