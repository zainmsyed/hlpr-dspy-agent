# Research: Save Document Summaries in Organized Folder Structure

## Decisions Made

### Folder Structure Location
**Decision**: Use `hlpr/summaries/documents/` relative to current working directory  
**Rationale**: 
- Provides predictable, organized location for users
- Follows existing project convention of `hlpr/` prefix (matches `.hlpr/` config directory pattern)
- Relative to CWD allows flexibility for different project contexts
- Easy to find and backup

**Alternatives Considered**:
- `~/.hlpr/summaries/documents/` - Rejected: Too hidden, harder to share/backup
- `./summaries/` - Rejected: Too generic, conflicts with user folders
- `./output/summaries/` - Rejected: Verbose, less discoverable

### Path Resolution Strategy
**Decision**: Default to organized structure, exact custom paths when `--output` specified  
**Rationale**:
- Maintains full backward compatibility
- Clear separation of concerns: organized by default, custom when requested
- No ambiguity about behavior

**Alternatives Considered**:
- Always use organized structure - Rejected: Breaks existing workflows
- Ask user for confirmation - Rejected: Interrupts automation

### Default File Format
**Decision**: Change default format from `txt` to `md` (Markdown)  
**Rationale**:
- Better formatting for summaries with headers, lists, emphasis
- More readable and portable than plain text
- Supports rich text while remaining human-readable
- Aligns with documentation best practices

**Alternatives Considered**:
- Keep txt - Rejected: Less readable for structured summaries
- Use json - Rejected: Not human-readable for primary use case

### Directory Creation Approach
**Decision**: Use `pathlib.Path.mkdir(parents=True, exist_ok=True)`  
**Rationale**:
- Standard library, no additional dependencies
- Atomic operation, handles race conditions
- Cross-platform compatibility
- Graceful handling of existing directories

**Alternatives Considered**:
- `os.makedirs()` - Works but pathlib is more modern
- Manual directory tree creation - Rejected: More error-prone

### Error Handling Strategy
**Decision**: Graceful degradation with clear error messages  
**Rationale**:
- Don't break user workflow due to folder issues
- Provide actionable error messages
- Allow fallback to current directory if needed

**Error Scenarios Addressed**:
- Permission denied for folder creation
- Disk space issues
- Invalid path characters
- Network drive unavailability

### File Overwrite Behavior
**Decision**: Maintain existing warning behavior  
**Rationale**:
- Consistent with current CLI behavior  
- Prevents accidental data loss
- User remains in control

## Technical Implementation Notes

### Core Changes Required
1. **Enhanced `_determine_output_path()` function**:
   - Check if `--output` specified → use exact path
   - Otherwise → construct `hlpr/summaries/documents/{filename}`
   - Create directory structure if needed

2. **New utility module `organized_storage.py`**:
   - `ensure_summary_directory()` - Create folder structure
   - `resolve_organized_path()` - Generate organized file paths
   - `validate_custom_path()` - Validate user-provided paths

3. **Enhanced error handling**:
   - Catch `PermissionError`, `OSError` during folder creation
   - Provide specific error messages with suggestions
   - Fallback gracefully when possible

### Backward Compatibility Guarantee
- Existing `--output /path/file.ext` behavior unchanged
- All existing CLI options continue to work
- Default behavior enhancement (when no `--output` specified)
- No breaking changes to API contracts

### Testing Strategy
1. **Contract Tests**: CLI behavior with/without `--output`
2. **Integration Tests**: File system operations, directory creation
3. **Unit Tests**: Path resolution logic, error handling
4. **Edge Case Tests**: Permissions, disk space, invalid paths

### Performance Considerations
- Directory creation is one-time cost per session
- Path resolution adds minimal overhead (<1ms)
- No impact on summary generation performance
- Folder existence check is cached by OS

## Dependencies Assessment

### New Dependencies Required
**None** - Feature uses only Python standard library:
- `pathlib` - Path manipulation and directory creation
- `os` - Environment variable access if needed
- Existing `typer`, `rich` for CLI enhancements

### Integration Points
- **CLI Module**: `src/hlpr/cli/summarize.py` - Primary integration point
- **Configuration**: Potential future extension for user preferences
- **Error Handling**: Leverage existing error handling patterns
- **Logging**: Use existing logging infrastructure

## Risk Assessment

### Low Risk
- Uses standard library functions
- No external service dependencies
- Minimal code changes required
- Well-defined error scenarios

### Mitigation Strategies
- Comprehensive test coverage for edge cases
- Graceful fallback to current directory
- Clear error messages with troubleshooting guidance
- Phased rollout with backward compatibility

## Future Extension Points
1. **Configuration Support**: User-customizable base directory
2. **Date-based Organization**: Optional date folders within structure
3. **Project-based Organization**: Organize by project/workspace
4. **Index Generation**: Metadata files for search/discovery
5. **Cleanup Tools**: Commands to manage old summaries

*Research completed: All technical decisions resolved, ready for design phase*