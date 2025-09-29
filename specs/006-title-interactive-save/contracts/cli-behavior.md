# Contract: CLI Interactive Save Behavior

Endpoint: `hlpr summarize document <file>` (CLI)

Behavior:
- When run without `--save`, the CLI prompts the user to confirm saving the generated summary. If confirmed, it prompts for format and destination path.
- In non-interactive contexts, the CLI auto-saves using defaults.

Output:
- On success: prints `Summary saved to: <path>`
- On decline: prints `Summary not saved.`
- On error: prints an error message and exits with non-zero code (see `StorageError` semantics)
