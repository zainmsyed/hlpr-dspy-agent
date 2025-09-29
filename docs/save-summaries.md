## Saving summaries to organized storage

The CLI supports `--save` to persist summaries in the organized `summaries/documents/` folder by default. When no custom `--output` path is provided the CLI will create `summaries/documents/` relative to the current working directory and save the summary there. Backward compatibility is preserved: if you pass `--output <path>` the CLI will write exactly to that path and will not use the organized folder.

By default, when saving the CLI uses Markdown format (`.md`) for saved summaries. You can override the format with `--format <txt|md|json>` when invoking the command.

To protect against low-disk scenarios you can supply `--min-free-mb <N>` to require at least N MiB free on the filesystem before the save will proceed. When the free space is too low the CLI exits with code 7 and prints a short Storage error message.

Example: `hlpr summarize document mydoc.md --save --min-free-mb 10`
