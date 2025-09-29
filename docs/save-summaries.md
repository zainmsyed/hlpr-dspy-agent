## Saving summaries to organized storage

The CLI supports `--save` to persist summaries in the organized `hlpr/summaries/...` folder. To protect against low-disk scenarios you can supply `--min-free-mb <N>` to require at least N MiB free on the filesystem before the save will proceed. When the free space is too low the CLI exits with code 7 and prints a short Storage error message.

Example: `hlpr summarize document mydoc.md --save --min-free-mb 10`
