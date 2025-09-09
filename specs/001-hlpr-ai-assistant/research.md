# Research: hlpr AI Assistant Implementation

## DSPy Framework Integration

**Decision**: Use DSPy 2.4+ with MIPRO optimizer for AI pipeline management
**Rationale**: 
- DSPy provides structured approach to LLM pipeline optimization
- MIPRO enables automatic prompt refinement for summarization tasks
- Built-in support for multiple LLM backends (OpenAI, Anthropic, custom)
- Allows systematic evaluation and improvement of AI workflows

**Alternatives considered**:
- LangChain: More heavyweight, less focused on optimization
- Direct LLM API calls: No optimization capabilities, more manual prompt engineering
- Haystack: Primarily for search/QA, not optimized for summarization

## Local LLM Integration Strategy

**Decision**: HTTP-based integration with Ollama as primary local backend
**Rationale**:
- Ollama provides standardized API compatible with OpenAI format
- User can manage their own models and hardware requirements
- No need to bundle models or handle GPU management in our application
- Allows fallback to cloud providers when local unavailable

**Alternatives considered**:
- Direct llama.cpp integration: Requires model management, GPU handling
- Hugging Face Transformers: Memory intensive, complex deployment
- vLLM server: More complex setup for personal use

## Document Parsing Strategy

**Decision**: Multiple specialized libraries for different formats
**Rationale**:
- PyPDF2 for PDF text extraction (simple, reliable for text-based PDFs)
- python-docx for DOCX files (standard library for Word documents)
- Built-in text/markdown handling (no additional dependencies)
- Clear error messages for unsupported formats (scanned PDFs)

**Alternatives considered**:
- Unstructured.io: Heavyweight, includes OCR which is out of scope
- pymupdf: More complex, includes rendering features we don't need
- pandoc: External dependency, format conversion rather than parsing

## Email Client Architecture

**Decision**: aioimaplib for async IMAP operations with keyring for credentials
**Rationale**:
- Async operations prevent CLI blocking during email fetching
- IMAP-only approach (read-only) simplifies security model
- System keyring integration provides secure credential storage
- Support for major providers (Gmail, Outlook) with app passwords

**Alternatives considered**:
- imaplib (built-in): Synchronous, would block CLI operations
- exchangelib: Exchange-specific, doesn't cover Gmail
- OAuth2 integration: Complex setup, out of scope for v1

## CLI Framework Selection

**Decision**: Typer + Rich for CLI interface
**Rationale**:
- Typer provides type-safe CLI with automatic help generation
- Rich enables beautiful terminal output with progress bars, tables, syntax highlighting
- Excellent integration between the two libraries
- Supports both guided and power-user modes

**Alternatives considered**:
- Click: Less type-safe, no built-in rich output
- argparse: Too low-level, requires manual help/validation
- Fire: Less control over interface design

## FastAPI Backend Design

**Decision**: Optional FastAPI server with same core libraries
**Rationale**:
- Reuse all core processing libraries (document, email, LLM)
- Standard REST API design for easy integration
- Built-in request validation and OpenAPI documentation
- Can run on localhost for personal use or deployed for team access

**Alternatives considered**:
- Flask: Less built-in validation, requires more boilerplate
- Django: Too heavyweight for this use case
- Custom HTTP server: Reinventing the wheel

## Chunking Strategy for Large Documents

**Decision**: Hierarchical chunking with configurable parameters
**Rationale**:
- Default 8192 tokens per chunk with 256 token overlap
- Process chunks individually, then summarize the summaries
- Configurable via CLI flags for different model context windows
- Preserves document structure better than simple splitting

**Alternatives considered**:
- Fixed-size splitting: Loses semantic coherence
- Paragraph-based chunking: Inconsistent sizes for token limits
- Sentence-based chunking: Too granular for long documents

## Testing Strategy

**Decision**: Multi-level testing with real dependencies
**Rationale**:
- Contract tests for API endpoints (fail first, then implement)
- Integration tests with real LLM endpoints using test prompts
- Unit tests for parsing and utility functions
- End-to-end tests using quickstart scenarios

**Test Environment Setup**:
- Mock local LLM server for consistent testing
- Test email account for IMAP integration tests
- Sample documents in multiple formats for parsing tests
- Isolated test configuration to avoid touching user credentials

## Configuration Management

**Decision**: YAML configuration with CLI overrides
**Rationale**:
- YAML for human-readable configuration files
- CLI flags can override config values for power users
- Separate credential storage in system keyring
- Environment variable support for CI/deployment

**Configuration Structure**:
```yaml
default_llm: "local"
local_llm_endpoint: "http://localhost:11434"
cloud_providers:
  openai:
    model: "gpt-4"
  anthropic:
    model: "claude-3-sonnet"
email_accounts:
  - id: "personal"
    provider: "gmail"
    username: "user@gmail.com"
    # password stored in keyring
```

## Performance Optimization

**Decision**: Streaming and async processing where possible
**Rationale**:
- Stream large file processing to show progress
- Async email operations to handle multiple accounts
- LLM request batching for multiple documents
- Caching of processed results to avoid re-processing

**Optimization Techniques**:
- Rich progress bars for long operations
- Concurrent processing of independent documents
- Smart chunking to minimize LLM API calls
- Result caching with content hashing