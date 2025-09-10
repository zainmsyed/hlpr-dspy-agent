# CLI Contract Specification: Document Summarization

## hlpr summarize document

**Usage**: `hlpr summarize document [OPTIONS] FILE_PATH`

**Description**: Summarize a document (PDF, DOCX, TXT, MD)

**Arguments**:
- `FILE_PATH`: Path to the document file to summarize (required)

**Options**:
- `--provider TEXT`: AI provider to use [local|openai|anthropic] (default: configured default)
- `--save / --no-save`: Save summary to file (default: False)
- `--format [txt|md|json]`: Output format (default: rich terminal output)
- `--output PATH`: Output file path (default: auto-generated)
- `--chunk-size INTEGER`: Chunk size for large documents (default: 8192)
- `--chunk-overlap INTEGER`: Overlap between chunks (default: 256)
- `--help`: Show help message

**Examples**:
```bash
hlpr summarize document report.pdf
hlpr summarize document --provider openai --save --format md notes.docx
hlpr summarize document --output summary.txt document.txt
```

**Output**:
- Rich terminal display with summary and key points
- Optional file output in specified format
- Progress bar for large documents
- Error messages for unsupported files

**Exit Codes**:
- 0: Success
- 1: File not found or unreadable
- 2: Unsupported file format
- 3: LLM provider unavailable
- 4: Processing error

## Global Options

Available for all commands:

- `--verbose / --no-verbose`: Enable verbose output (default: False)
- `--quiet / --no-quiet`: Suppress non-essential output (default: False)
- `--config PATH`: Custom configuration file path
- `--help`: Show help message
- `--version`: Show version information

## Exit Codes

Standard exit codes used across all commands:

- `0`: Success
- `1`: General error (file not found, invalid input, etc.)
- `2`: Configuration error (missing config, invalid settings)
- `3`: Authentication error (invalid credentials, API key)
- `4`: Network error (connection failed, timeout)
- `5`: Provider error (LLM unavailable, quota exceeded)
- `6`: Processing error (parsing failed, unsupported format)