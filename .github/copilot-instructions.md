# Copilot Instructions for hlpr AI Agent

## Development Guidelines

### Package Management with UV
```bash
# Add dependencies
uv add package-name

# Development dependencies  
uv add --dev pytest ruff

# Run commands
uv run python -m src.cli check-setup
uv run pytest
uvx run ruff check  # Linting
uvx run ruff format  # Formatting
```
always use uv add for adding dependencies to pyproject.toml

# Local DSPy / Local model developer notes

This project supports multiple LLM providers (local, openai, anthropic, groq, together).
Local providers have different performance and startup characteristics than cloud providers.
This short note documents the policy and how to avoid accidental timeouts for local models.

Why this matters
-----------------
- Local models may take longer to start and may have non-deterministic latency.
- CI and unit tests often mock or bypass LLM calls; however, running the real app against
  a local LLM in development can be slow and should not be interrupted by hard-coded
  timeouts unless explicitly configured.

Policy
------
- For provider="local" the codebase **defaults to no timeout** (i.e. wait indefinitely)
  when the caller does not explicitly pass a `timeout` value. This avoids spurious
  SummarizationError timeouts during normal local development.
- For remote/cloud providers we keep the configured `CONFIG.default_timeout` and
  `fast_fail_seconds` behavior to protect CI and networked runs.
- DSPy integration will retry transient errors up to 3 attempts before failing.

Files/behavior changed
----------------------
- `src/hlpr/document/summarizer/__init__.py`
  - When `provider=='local'` and `timeout is None` the summarizer uses `timeout=None`.
- `src/hlpr/llm/dspy_integration.py`
  - `_result_from_future` does not enforce timeouts for the local provider (blocks until
    the underlying call completes or raises). Retry attempts were increased to 3.

How to run locally
-------------------
Use the project's venv python (the tests expect `src` on PYTHONPATH):

```bash
# parse & summarize a file (example)
/home/zain/Documents/coding/hlpr/.venv/bin/python - <<'PY'
from hlpr.document.parser import DocumentParser
from hlpr.document.summarizer import DocumentSummarizer
from hlpr.models.document import Document

path = 'documents/examples/welcome_to_wrtr.md'
text = DocumentParser.parse_file(path)
doc = Document.from_file(path)
doc.extracted_text = text
summarizer = DocumentSummarizer(provider='local', timeout=None)
result = summarizer.summarize_document(doc)
print(result.summary)
PY
```

Testing and CI recommendations
-----------------------------
- Add unit tests that assert the local-provider default behavior so future refactors
  don't reintroduce timeouts. See `tests/unit/test_local_provider_timeout.py`.
- In CI, prefer mocking `dspy.Predict` or set configuration to use deterministic
  fallback summarizer to avoid long-running external calls.
- If running integration tests that need a real DSPy backend, gate them with a marker
  (e.g., `pytest -m dspy`) so they only run in environments with DSPy available.

Developer checklist
-------------------
1. When changing anything in DSPy or summarizer code, ensure a unit test verifies
   the `timeout` semantics for `provider='local'`.
2. If you need to enforce a timeout for local models (e.g., CI), do so explicitly
   by passing `timeout=<seconds>` to `DocumentSummarizer` or configuring `CONFIG.default_timeout`.
3. Keep retry logic configurable if desired; currently it is 3 attempts.

If anything here is unclear or you'd like this behavior changed (for example, make
timeouts configurable per-environment), I can add a config flag and tests to enforce it.
