(# hlpr — Document Summarization)

This repository contains hlpr, a small document processing and summarization toolkit.

CLI: hlpr summarize document

Options (high level):
- --provider: AI provider to use (local|openai|anthropic|groq|together)
- --model: Model name (e.g., gemma3:latest)
- --temperature: Sampling temperature for the model (0.0-1.0). Default is 0.3.
- --dspy-timeout: DSPy request timeout in seconds
- --verify-hallucinations: Enable optional model-backed verification for flagged sentences

Examples:

Summarize a markdown file with default settings:

	hlpr summarize document documents/examples/welcome_to_wrtr.md

Summarize with a deterministic output (temperature 0.0):

	hlpr summarize document documents/examples/welcome_to_wrtr.md --temperature 0.0

API: POST /summarize/document

You can supply an optional `temperature` field in the JSON body or as a query parameter. When omitted, the server defaults to 0.3.


Logging and correlation IDs
---------------------------

hlpr emits structured logs enriched with a correlation ID so you can trace a request end-to-end across the API, CLI, and DSPy layers. Behavior is controlled via environment variables:

- HLPR_INCLUDE_FILE_PATHS (default: false)
	- When true, logs may include user-provided file names. Filenames are sanitized to basenames (no full paths).
- HLPR_INCLUDE_TEXT_LENGTH (default: true)
	- When true, logs for text requests include the length of the input text.
- HLPR_INCLUDE_CORRELATION_HEADER (default: true)
	- When true, API responses include the header `X-Correlation-ID` so callers can correlate client logs with server logs.
- HLPR_PERFORMANCE_LOGGING (default: true)
	- When true, logs include simple timing metrics like `processing_time_ms` for completed operations.

Example API response headers (when enabled):

		X-Correlation-ID: 3fb1c4f4-2c7b-4c69-8519-1b8d2fd0f5ac

Notes:
- Filename logging always uses the basename via sanitization to avoid leaking local filesystem paths.
- Long error messages are truncated in logs to keep entries small and readable.


CORS configuration
------------------

By default hlpr restricts CORS to local origins to avoid accidentally
enabling wide-open CORS in production. You can override allowed origins
using the `HLPR_ALLOWED_ORIGINS` environment variable. Examples:

- Allow localhost (default): leave `HLPR_ALLOWED_ORIGINS` unset
- Allow a specific origin: `HLPR_ALLOWED_ORIGINS=https://example.com`
- Allow multiple origins: `HLPR_ALLOWED_ORIGINS=https://a.com,https://b.com`
- Allow all origins (development only): `HLPR_ALLOWED_ORIGINS=*`

Set the environment variable before starting the server. For example:

	export HLPR_ALLOWED_ORIGINS="https://example.com"

