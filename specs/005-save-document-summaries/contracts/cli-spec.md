# CLI Contract Specification: Organized Summary Storage

## hlpr summarize document (Enhanced)

**Usage**: `hlpr summarize document [OPTIONS] FILE_PATH`

**Description**: Summarize a document with organized folder storage

**Arguments**:
- `FILE_PATH`: Path to the document file to summarize (required)

**Options** (Enhanced):
- `--provider TEXT`: AI provider to use [local|openai|anthropic|groq|together] (default: local)
- `--save / --no-save`: Save summary to organized folder structure (default: False)
- `--format [txt|md|json]`: Output format (default: md) *CHANGED from txt*
- `--output PATH`: Custom output file path (bypasses organized structure)
- `--chunk-size INTEGER`: Chunk size for large documents (default: 8192)
- `--chunk-overlap INTEGER`: Overlap between chunks (default: 256)
- `--help`: Show help message

**New Behavior**:
```bash
# Default: Saves to hlpr/summaries/documents/
hlpr summarize document report.pdf --save
# → Creates: hlpr/summaries/documents/report_summary.md

# Custom path: Bypasses organized structure
hlpr summarize document report.pdf --save --output /tmp/my_summary.txt
# → Creates: /tmp/my_summary.txt (exact path)

# Format selection with organized structure
hlpr summarize document report.pdf --save --format json
# → Creates: hlpr/summaries/documents/report_summary.json
```

**Success Criteria**:
1. When `--save` used without `--output`: Creates `hlpr/summaries/documents/` and saves there
2. When `--save` used with `--output`: Uses exact custom path, ignores organized structure
3. Directory creation fails gracefully with clear error message
4. File overwrite warning behavior unchanged
5. All existing output formats supported in organized structure

**Error Handling**:
- Permission denied → Clear error message with suggested solutions
- Disk space issues → Graceful fallback with warning
- Invalid custom path → Validation error with path requirements
- Directory creation failure → Fallback to current directory with warning

## File System Contract

### Organized Structure Creation
```
Working Directory/
└── hlpr/                    # Created if missing
    └── summaries/           # Created if missing  
        └── documents/       # Created if missing
            └── {name}_summary.{ext}  # Summary file
```

### Path Resolution Contract
```python
# Interface contract for path resolution
def determine_output_path(
    document_path: str,
    custom_output: Optional[str],
    format: str,
    base_dir: Path = Path.cwd()
) -> Path:
    """
    Resolve final output path for summary.
    
    Args:
        document_path: Source document file path
        custom_output: User-specified output path (or None)
        format: Output format (txt, md, json)
        base_dir: Base directory for organized structure
    
    Returns:
        Path: Final resolved path for saving summary
    
    Behavior:
        - If custom_output provided: return Path(custom_output) exactly
        - Otherwise: return base_dir/hlpr/summaries/documents/{stem}_summary.{format}
    """
```

### Directory Creation Contract
```python
def ensure_summary_directories(base_path: Path) -> bool:
    """
    Create organized directory structure.
    
    Args:
        base_path: Base directory for structure creation
    
    Returns:
        bool: True if directories exist/created successfully, False otherwise
    
    Behavior:
        - Creates base_path/hlpr/summaries/documents/ 
        - Uses parents=True, exist_ok=True
        - Returns False on permission/disk space errors
        - Does not raise exceptions
    """
```

## Error Response Contract

### Directory Creation Errors
```
Error Type: DirectoryCreationError
Message: "Cannot create summary directory at {path}: {reason}"
Suggestions:
- Check directory permissions
- Verify available disk space  
- Try alternative location with --output
Exit Code: 1
```

### Path Validation Errors
```
Error Type: PathValidationError  
Message: "Invalid output path '{path}': {reason}"
Suggestions:
- Use valid file path characters
- Ensure parent directory exists
- Check path length limits
Exit Code: 1
```

### Permission Errors
```
Error Type: PermissionError
Message: "Permission denied accessing {path}"
Suggestions:
- Check file/directory permissions
- Run with appropriate privileges
- Use alternative location with --output
Exit Code: 1
```

## Backward Compatibility Contract

### Existing Behavior Preserved
- All current CLI options work identically
- `--output` parameter behavior unchanged
- File overwrite warnings unchanged  
- Error handling patterns consistent
- API response formats unchanged

### Enhanced Behavior (Non-Breaking)
- Default format changed: txt → md (enhancement, not breaking)
- New organized storage only when `--save` used without `--output`
- Additional success messages for directory creation
- Enhanced error messages with more context

## Testing Contract

### Required Tests
1. **Organized Structure Creation**:
   - `test_creates_organized_directories()`
   - `test_saves_to_organized_path()`
   - `test_organized_path_with_different_formats()`

2. **Custom Path Behavior**:
   - `test_custom_output_bypasses_organized_structure()`
   - `test_custom_output_creates_exact_path()`

3. **Error Handling**:
   - `test_permission_denied_handling()`
   - `test_disk_space_error_handling()`
   - `test_invalid_path_handling()`

4. **Backward Compatibility**:
   - `test_existing_workflows_unchanged()`
   - `test_all_formats_supported()`
   - `test_overwrite_warnings_preserved()`

### Test Data Requirements
- Sample documents in various formats (PDF, DOCX, TXT, MD)
- Test directories with different permission levels
- Mock file system scenarios for error testing
- Temporary directories for isolated testing

*CLI contract complete: All behaviors specified with clear success/error conditions*