# Quickstart: Interactive Save Prompt

1. Run a document summarization without `--save` to trigger interactive prompts:

```bash
hlpr summarize document documents/examples/cover_letter.md
```

2. After the summary is displayed you will be prompted:
- "Would you like to save the summary? (yes/no) [Y]: " (default Yes)
- If yes: "Format to save as (md/txt/json) [md]: " (default md)
- Then: "Destination path to save the summary [<default path>]: " (default is organized storage path)

3. Non-interactive runs (CI) detect non-TTY and auto-save with defaults (yes, md, default path).
