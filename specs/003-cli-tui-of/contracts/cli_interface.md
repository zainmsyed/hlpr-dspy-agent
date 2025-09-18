# CLI Interface Contracts

This directory contains the interface contracts for the enhanced CLI/TUI functionality.

## Command Contracts

### Guided Mode Command: `hlpr summarize`

**Signature**: `hlpr summarize [OPTIONS]`

**Options**:
- `--help`: Show help and exit
- `--config PATH`: Use specific config file
- `--verbose`: Enable verbose output during guided mode

**Behavior Contract**:
1. **MUST** present file selection interface using Rich table/list
2. **MUST** validate selected files before proceeding  
3. **MUST** present provider selection with availability status
4. **MUST** show preview of processing options before confirmation
5. **MUST** display progress using Rich progress bars with phases
6. **MUST** present results in formatted Rich panels
7. **MUST** offer to save results with format selection
8. **MUST** handle Ctrl+C gracefully with option to save partial results

**Exit Codes**:
- 0: Successful completion
- 1: User cancellation
- 2: Invalid input/configuration
- 3: Processing error with partial results available
- 4: Fatal processing error

### Enhanced Direct Command: `hlpr summarize document`

**Signature**: `hlpr summarize document [FILES]... [OPTIONS]`

**Arguments**:
- `FILES`: One or more file paths or glob patterns (required)

**Options**:
- `--provider TEXT`: AI provider [local|openai|anthropic|groq|together] (default: local)
- `--format TEXT`: Output format [rich|txt|md|json] (default: rich)
- `--save`: Save output to file
- `--output PATH`: Output file path (auto-generated if not specified)
- `--batch`: Process multiple files in parallel
- `--verbose`: Show detailed processing information
- `--temperature FLOAT`: Model temperature (0.0-1.0, default: 0.3)
- `--model TEXT`: Specific model name
- `--chunk-size INT`: Chunk size for large documents (default: 8192)
- `--chunk-overlap INT`: Overlap between chunks (default: 256)
- `--chunking-strategy TEXT`: Strategy [sentence|paragraph|fixed|token] (default: sentence)
- `--timeout INT`: Processing timeout in seconds
- `--no-fallback`: Disable fallback to alternative providers
- `--verify-hallucinations`: Enable hallucination verification

**Behavior Contract**:
1. **MUST** validate all file paths before processing begins
2. **MUST** display Rich progress bars for processing phases
3. **MUST** process multiple files in parallel when `--batch` specified
4. **MUST** continue processing remaining files if one fails
5. **MUST** display results using Rich formatting (when format=rich)
6. **MUST** save to file when `--save` specified
7. **MUST** show processing metadata in verbose mode
8. **MUST** handle interruptions gracefully

**Exit Codes**:
- 0: All files processed successfully
- 1: File not found or access denied
- 2: Unsupported file format
- 3: Provider/configuration error
- 4: Processing failed for some files (partial success)
- 5: Processing failed for all files
- 6: Output write error

## Interactive Flow Contracts

### File Selection Interface

**Input Contract**:
- **MUST** accept file paths via typing or selection
- **MUST** support glob patterns (*.pdf, documents/*.txt, etc.)
- **MUST** show file browser-like interface with Rich tables
- **MUST** display file size, format, and validity status

**Output Contract**:
```python
selected_files: List[FileSelection]
```

**Error Handling**:
- Invalid paths: Show error message and retry
- No files selected: Prompt for at least one file
- All files invalid: Show error summary and exit option

### Provider Selection Interface

**Input Contract**:
- **MUST** show available providers with status (available/unavailable)
- **MUST** show provider descriptions and capabilities
- **MUST** allow model selection for chosen provider
- **MUST** validate provider availability before proceeding

**Output Contract**:
```python
provider_config: {
    "provider": str,
    "model": str,
    "temperature": float,
    "additional_options": Dict[str, Any]
}
```

**Error Handling**:
- Provider unavailable: Show alternatives
- Invalid model: Show available models
- Configuration error: Show configuration help

### Options Configuration Interface

**Input Contract**:
- **MUST** show current configuration summary
- **MUST** allow modification of key settings (temperature, output format, chunking)
- **MUST** provide sensible defaults
- **MUST** validate parameter ranges

**Output Contract**:
```python
output_preferences: OutputPreferences
processing_options: Dict[str, Any]
```

## Progress Display Contracts

### Progress Bar Requirements

**Visual Contract**:
- **MUST** show current phase (Parsing, Chunking, Summarizing)
- **MUST** display percentage completion when determinable
- **MUST** show elapsed time
- **MUST** show current file being processed (in batch mode)
- **MUST** use appropriate Rich styling (colors, spinners)

**Update Contract**:
```python
def update_progress(
    phase: str,           # Current processing phase
    progress: float,      # 0.0 to 1.0, or None if indeterminate
    message: str,         # Current operation description
    file_path: Optional[str] = None  # Current file (batch mode)
):
    """Update progress display"""
```

### Error Display Requirements

**Error Panel Contract**:
- **MUST** use Rich panels with appropriate styling
- **MUST** show error type and user-friendly message
- **MUST** provide actionable suggestions
- **MUST** show technical details in verbose mode
- **MUST** offer options to continue, retry, or abort

## Output Format Contracts

### Rich Terminal Output

**Structure Contract**:
```
┌─ Summary ─┐
│ [summary text] │
└────────────────┘

┌─ Key Points ─┐
│ • Point 1    │
│ • Point 2    │
└──────────────┘

┌─ Metadata ─┐
│ File: filename.pdf │
│ Provider: local    │
│ Time: 1.2s        │
└───────────────────┘
```

### JSON Output Contract

```json
{
  "results": [
    {
      "file_path": "path/to/file.pdf",
      "summary": "Summary text...",
      "key_points": ["Point 1", "Point 2"],
      "metadata": {
        "file_size_bytes": 12345,
        "provider": "local",
        "model": "gemma3:latest",
        "processing_time_ms": 1200,
        "chunk_count": 3
      }
    }
  ],
  "processing_summary": {
    "total_files": 1,
    "successful": 1,
    "failed": 0,
    "total_time_ms": 1200
  }
}
```

### Markdown Output Contract

```markdown
# Document Summary: filename.pdf

**File**: filename.pdf  
**Provider**: local  
**Processing Time**: 1.2s

## Summary

[Summary text...]

## Key Points

- Point 1
- Point 2

## Metadata

- **Format**: PDF
- **Size**: 12.3 KB
- **Chunks**: 3
```

## Validation Contracts

### File Validation

**Input**: File path or glob pattern  
**Output**: FileSelection object with validity status

**Requirements**:
- **MUST** check file existence
- **MUST** check file readability
- **MUST** detect file format
- **MUST** validate file size against limits
- **MUST** provide clear error messages for invalid files

### Configuration Validation

**Input**: CLI arguments and options  
**Output**: Validated configuration objects

**Requirements**:
- **MUST** validate provider availability
- **MUST** check parameter ranges (temperature, chunk sizes)
- **MUST** verify output path writability
- **MUST** validate format compatibility
- **MUST** provide helpful error messages with suggestions