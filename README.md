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

