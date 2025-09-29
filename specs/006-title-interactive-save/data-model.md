# Data Model: Saved Summary

This feature introduces a lightweight conceptual model for saved summaries used primarily for file naming and metadata when saving in JSON format.

Entity: SavedSummary
- `path` (string): Filesystem path where the summary is stored
- `format` (enum: md|txt|json): Output format
- `generated_at` (ISO8601 string): Timestamp when saved
- `summary` (string): The textual summary content
- `source_file` (string): Original document filename

Validation:
- `format` must be one of `md`, `txt`, `json`
- `path` must be a writable location or its parent directory must be creatable
