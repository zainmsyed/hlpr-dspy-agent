# hlpr — Document Summarization

Personal AI assistant for document summarization with a beautiful CLI/TUI experience.

## Quick Start

Follow these minimal steps to get the project running locally.

1) Install uv (recommended)

   Follow the official guide: https://docs.astral.sh/uv/getting-started/installation/


2) Clone and install

```bash
git clone https://github.com/zainmsyed/hlpr-dspy-agent.git
cd hlpr
# create virtual environment and install baseline dependencies with uv
uv sync
```

For most users (minimal runtime install)

```bash
# editable install (useful for local tweaks without dev extras)
pip install -e .

# production install
pip install .

# per-user isolated CLI install (recommended)
pipx install .
```


Optional: contributor / developer setup (dev tooling)

```bash
# preferred: sets up the development environment with uv
uv sync --group dev

# or with pip (editable install + dev extras)
pip install -e .[dev]
```

3) Try it out

```bash
# Summarize a single document (rich terminal output)
hlpr summarize document test_document.txt

# Get JSON output
hlpr summarize document test_document.txt --format json

# Process multiple files and write markdown summaries
hlpr summarize documents *.txt --format md

```
## Temperature example

`--temperature` controls sampling randomness for model output. Lower values (0.0) make output deterministic; higher values (e.g., 0.7) increase creativity/diversity.

```bash
# Deterministic output (less creative, repeatable)
hlpr summarize document documents/examples/welcome_to_wrtr.md --temperature 0.0 

# More diverse output (more creative / varied)
hlpr summarize document documents/examples/welcome_to_wrtr.md --temperature 0.7 

```


4) See all options

```bash
hlpr --help
hlpr summarize --help
```

For detailed documentation and API reference, see `documents/detailed-readme.md`.


## Common Commands

```bash
# Summarize a document (JSON output)
hlpr summarize document documents/examples/welcome_to_wrtr.md --provider local --format json

# Guided mode with phase-aware progress
hlpr summarize guided documents/examples/welcome_to_wrtr.md --provider local --format rich

# Save output to a file (auto filename or explicit path)
hlpr summarize document test_document.txt --save --format md
hlpr summarize document test_document.txt --save --output my_summary.json --format json

Note: When using `--save` without `--output`, hlpr will create an organized
folder `summaries/documents/` in the current working directory and write
the summary there. By default saved summaries use Markdown (`.md`) unless you
specify `--format`.
```

## Notes for local development

- For `provider=local`, the summarizer defaults to no timeout when not explicitly provided; pass `--dspy-timeout` if you want to enforce one. See `documents/local-dspy.md` for more details.
- When piping to another process (e.g., `| jq ...`), prefer `--format json` to avoid ANSI sequences.

## Testing interactive CLI

Some CLI commands are interactive by default. For automated tests (CI) you can
simulate prompt responses by setting the environment variable
`HLPR_SIMULATED_PROMPTS` to a newline-separated list of responses. The CLI will
consume these values in order and fall back to real interactive prompts when the
variable is not set.

Example (pytest / monkeypatch):

```py
def test_setup_non_interactive(monkeypatch, tmp_path):
   monkeypatch.setenv("HOME", str(tmp_path))
   # provider (enter), format (enter), temperature, max_tokens
   monkeypatch.setenv("HLPR_SIMULATED_PROMPTS", "\n\n0.3\n8192")
   # call the setup function directly or invoke the CLI
   from hlpr.cli.config import setup_config
   try:
      setup_config(non_interactive=False)
   except Exception:
      # typer raises click.exceptions.Exit on success; ignore in tests
      pass

```

This approach keeps interactive flows testable and avoids hanging CI runs.

## Troubleshooting

- File not found: check the path or use an absolute path.
- Unsupported file format: use PDF, DOCX, TXT, or MD.
- Provider unavailable: try `--provider local` or configure credentials for the chosen provider.

---

## API: POST /summarize/document

The API supports a `temperature` parameter in the JSON body or as a query parameter. When omitted, the server defaults to `0.3`.

## Logging and correlation IDs

hlpr emits structured logs enriched with a correlation ID so you can trace a request end-to-end across the API, CLI, and DSPy layers. Behavior is controlled via environment variables described in the project documentation.

## CORS configuration

By default hlpr restricts CORS to local origins. Override allowed origins with the `HLPR_ALLOWED_ORIGINS` environment variable.

For the full API reference and configuration examples, see `documents/detailed-readme.md`.

