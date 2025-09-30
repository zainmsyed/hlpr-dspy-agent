## Saving summaries to organized storage

The CLI supports `--save` to persist summaries in the organized `summaries/documents/` folder by default. When no custom `--output` path is provided the CLI will create `summaries/documents/` relative to the current working directory and save the summary there. Backward compatibility is preserved: if you pass `--output <path>` the CLI will write exactly to that path and will not use the organized folder.

By default, when saving the CLI uses Markdown format (`.md`) for saved summaries. You can override the format with `--format <txt|md|json>` when invoking the command.

To protect against low-disk scenarios you can supply `--min-free-mb <N>` to require at least N MiB free on the filesystem before the save will proceed. When the free space is too low the CLI exits with code 7 and prints a short Storage error message.

Example: `hlpr summarize document mydoc.md --save --min-free-mb 10`

Interactive save flow

- When you run `hlpr summarize document <file>` without `--save` and you are in a TTY
	the CLI will display the summary and then prompt to save. This provides a privacy-first
	interactive experience where you explicitly confirm whether to persist results.

Non-interactive behavior and HLPR_AUTO_SAVE

- By default non-interactive runs (no TTY) will NOT save automatically to avoid
	accidental data retention in automation.
- To opt-in in automation, set `HLPR_AUTO_SAVE=true` in the environment. When set the
	CLI will save using the default choices (format=md, organized storage path).

Collision handling and atomic writes

- If the target file already exists the CLI will not overwrite it silently. Instead a
	timestamped filename is created using the format `_YYYYMMDDTHHMMSS` appended before
	the extension.
- All writes use an atomic write helper to avoid partially written or corrupt files.
	If an error occurs a `StorageError` is raised and the CLI prints a friendly message
	and non-zero exit code.
