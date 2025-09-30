# Quickstart: Interactive Save Prompt

1. Run a document summarization without `--save` to trigger interactive prompts:

```bash
hlpr summarize document documents/examples/cover_letter.md
```

2. After the summary is displayed you will be prompted:
- "Would you like to save the summary? (yes/no) [Y]: " (default Yes)
- If yes: "Format to save as (md/txt/json) [md]: " (default md)
- Then: "Destination path to save the summary [<default path>]: " (default is organized storage path)

3. Non-interactive runs (CI) are privacy-first: when running without a TTY the CLI will NOT
	save automatically unless you opt-in via the environment variable `HLPR_AUTO_SAVE=true`
	or by passing `--save` and an `--output` path on the command line. When `HLPR_AUTO_SAVE=true`
	the CLI uses the same defaults as interactive mode (format=md, organized storage path).
