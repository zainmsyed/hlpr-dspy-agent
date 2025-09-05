# Copilot Instructions for hlpr AI Agent

## Project Overview
**hlpr** is a privacy-first, modular AI assistant that processes emails, documents, and meeting transcripts locally using DSPy and Ollama. It provides intelligent categorization, summarization, and action item extraction without sending sensitive data to external services.

## Technology Stack
- **Framework**: DSPy for structured AI workflows
- **Models**: Ollama for local LLM inference (Llama 3.1, Mistral)
- **CLI**: Typer with Rich for beautiful terminal output
- **Package Management**: UV for fast Python dependency management
- **Data Models**: Pydantic for type-safe data structures
- **Architecture**: Modular workflow-based design

## Core Architecture Principles

### 1. Modular Workflow Design
- Each workflow (email, document, meeting) is completely independent
- Workflows inherit from `BaseWorkflow` or `OptimizableWorkflow`
- Clean separation between DSPy signatures, models, and processing logic

### 2. Privacy-First Local Processing
- All processing happens locally via Ollama
- Zero external API calls during operation
- Data never leaves the user's machine

### 3. DSPy Best Practices
- Use clean, well-defined signatures for each task
- Structured input/output with Pydantic models
- Modular DSPy programs for composability

## File Structure & Conventions

```
src/
├── core/                  # Base classes, models, exceptions
├── workflows/            # Independent processing workflows
│   ├── email/           # Email categorization & analysis
│   ├── documents/       # Document summarization
│   └── meetings/        # Meeting transcript processing
├── integrations/        # External service integrations (Ollama)
├── cli/                 # Typer-based command line interface
└── utils/               # Logging, helpers, formatting
```

### Key Components
- **Workflows**: Inherit from `BaseWorkflow[InputType, OutputType]`
- **Models**: Use Pydantic with clear field descriptions
- **Signatures**: DSPy signatures define input/output structure
- **CLI Commands**: Organized by domain (email, document, setup)

## Development Guidelines

### Package Management with UV
```bash
# Add dependencies
uv add package-name

# Example: add pydantic and python-dotenv (use uv, not manual edits to pyproject)
uv add pydantic
uv add python-dotenv

# Development dependencies  
uv add --dev pytest ruff

# Run commands
uv run python -m src.cli check-setup
uv run pytest
uvx run ruff check  # Linting
uvx run ruff format  # Formatting
```

### Code Style & Quality
- Use **Ruff** for formatting, linting, and import sorting (100 char line length)
- **Pydantic** models for all data structures
- **Type hints** required for all functions
- **Rich** for beautiful CLI output
- **Comprehensive error handling** with custom exceptions

### Workflow Implementation Pattern
1. Define Pydantic models for input/output in `models.py`
2. Create DSPy signatures in `signatures.py`  
3. Implement workflow class inheriting from `BaseWorkflow`
4. Add CLI commands in appropriate command module
5. Write comprehensive tests

## Key Implementation Details

### Email Workflow Structure
```python
# Input/Output models with Pydantic
class EmailInput(WorkflowInput):
    subject: str
    body: str
    sender: str
    # ...

# DSPy signature
class EmailCategorizationSignature(dspy.Signature):
    email_subject = dspy.InputField(desc="...")
    category = dspy.OutputField(desc="...")
    # ...

# Workflow implementation
class EmailCategorizationWorkflow(OptimizableWorkflow[EmailInput, EmailCategorizationOutput]):
    def process(self, input_data: EmailInput) -> EmailCategorizationOutput:
        # Implementation
```

### Ollama Integration
- Centralized `OllamaManager` for model lifecycle
- Connection verification and automatic model pulling
- DSPy integration via custom `OllamaLM` wrapper
- Configurable via environment variables

### CLI Design
- **Typer** with Rich markup support
- Commands organized by domain (`email`, `setup`, `models`)
- Consistent help text and error handling
- Progress indicators for long-running operations

## Testing Strategy
- **Unit tests** for individual workflows and components
- **Integration tests** for end-to-end workflow processing
- **Mock Ollama responses** for deterministic testing
- **CLI testing** with Typer's test client

## Configuration Management
- **Pydantic Settings** for environment-based configuration
- **`.env` file support** for local development
- **Sensible defaults** for all configuration options

## Error Handling
- Custom exception hierarchy (`WorkflowError`, `ValidationError`, etc.)
- Graceful degradation when models unavailable
- Comprehensive logging with structured output

## Performance Considerations
- **Batch processing** capabilities for multiple items
- **Timeout handling** for model requests
- **Memory-efficient** processing for large documents
- **Progress tracking** for user feedback

## Extension Points
- Easy to add new workflow types following existing patterns
- Plugin architecture for custom processing steps
- API-ready design for future web interface
- Optimization framework ready for MIPRO integration

## Common Patterns to Follow

### When creating new workflows:
1. Start with clear Pydantic models
2. Define DSPy signature with descriptive field names
3. Implement validation methods
4. Add comprehensive error handling
5. Include CLI commands with rich output
6. Write tests with mocked dependencies

### When working with DSPy:
- Use descriptive field descriptions for better LLM understanding
- Implement proper signature validation
- Handle model response parsing robustly
- Consider confidence scoring and reasoning outputs

### When building CLI features:
- Use Rich for beautiful, informative output
- Provide progress indicators for long operations
- Include helpful error messages with suggested fixes
- Support both interactive and batch modes

This is a sophisticated AI agent framework prioritizing privacy, modularity, and excellent developer experience. Focus on maintaining these principles while extending functionality.