# Quickstart: Enhanced CLI/TUI for Document Summarization

## Overview

This quickstart demonstrates the enhanced CLI/TUI experience for document summarization, covering both guided interactive mode and direct command usage.

## Prerequisites

- hlpr installed and configured
- At least one AI provider available (local or cloud)
- Sample documents for testing (PDF, DOCX, TXT, or MD files)

## Test Scenarios

### Scenario 1: Guided Mode (Beginner-Friendly)

**Objective**: Walk through the complete guided experience for first-time users.

**Steps**:
1. **Start guided mode**:
   ```bash
   hlpr summarize
   ```

2. **Expected**: Rich-formatted welcome screen with options:
   - File selection interface
   - Help text explaining the process
   - Option to exit or continue

3. **File Selection**:
   - Interface should display available files in a Rich table
   - Should support typing file paths
   - Should validate files and show status (✓ Valid, ✗ Invalid)
   - Should allow multiple file selection

4. **Provider Selection**:
   - Should show available providers with status
   - Should display provider descriptions
   - Should show model options for selected provider
   - Should validate availability before proceeding

5. **Options Configuration**:
   - Should show current settings summary
   - Should allow temperature adjustment (0.0-1.0)
   - Should allow output format selection (rich, txt, md, json)
   - Should allow save-to-file option

6. **Processing**:
   - Should display Rich progress bar with phases:
     - "Parsing document..."
     - "Chunking content..." (if needed)
     - "Generating summary..."
   - Should show elapsed time
   - Should be interruptible with Ctrl+C

7. **Results Display**:
   - Should show formatted summary in Rich panels
   - Should display key points in bullet format
   - Should show processing metadata
   - Should offer save options

**Validation**:
- All interactions should be keyboard-driven
- Error messages should be helpful and actionable
- Progress should be visually clear and informative
- Output should be beautifully formatted

### Scenario 2: Direct Command (Power User)

**Objective**: Test efficient direct command execution for experienced users.

**Test Case 2.1 - Single File with Defaults**:
```bash
hlpr summarize document test_document.pdf
```

**Expected Results**:
- Immediate processing with minimal prompts
- Rich progress bar during processing
- Formatted output in terminal
- Exit code 0 on success

**Test Case 2.2 - Custom Provider and Format**:
```bash
hlpr summarize document test_document.pdf --provider local --format json --save
```

**Expected Results**:
- Uses specified provider
- Outputs in JSON format
- Saves to auto-generated filename
- Shows confirmation message with saved file path

**Test Case 2.3 - Batch Processing**:
```bash
hlpr summarize document *.pdf --batch --format md --output summaries/
```

**Expected Results**:
- Processes all PDF files in parallel
- Shows progress for each file
- Saves each summary as markdown in summaries/ directory
- Continues processing if one file fails

**Test Case 2.4 - Verbose Mode**:
```bash
hlpr summarize document test_document.pdf --verbose --temperature 0.0
```

**Expected Results**:
- Shows detailed processing information
- Displays configuration details
- Shows chunking decisions (if applicable)
- Uses deterministic output (temperature 0.0)

### Scenario 3: Error Handling

**Test Case 3.1 - File Not Found**:
```bash
hlpr summarize document nonexistent.pdf
```

**Expected Results**:
- Clear error message in Rich panel
- Suggestion to check file path
- Exit code 1
- No processing attempted

**Test Case 3.2 - Unsupported Format**:
```bash
hlpr summarize document test_file.xyz
```

**Expected Results**:
- Error message listing supported formats
- Suggestion for conversion tools
- Exit code 2
- Graceful handling without crash

**Test Case 3.3 - Provider Unavailable**:
```bash
hlpr summarize document test.pdf --provider unavailable_provider
```

**Expected Results**:
- Error message about provider availability
- List of available providers
- Option to use fallback provider
- Exit code 3

**Test Case 3.4 - Processing Interruption**:
```bash
hlpr summarize document large_document.pdf
# Press Ctrl+C during processing
```

**Expected Results**:
- Graceful interruption handling
- Option to save partial results
- Clean cleanup of temporary files
- Exit code 1 (user cancellation)

### Scenario 4: Configuration Integration

**Test Case 4.1 - Config File Override**:
1. Set default provider in config:
   ```bash
   hlpr config set default_provider openai
   ```

2. Override with CLI flag:
   ```bash
   hlpr summarize document test.pdf --provider local
   ```

**Expected Results**:
- Uses local provider (CLI flag takes precedence)
- Shows active config in verbose mode
- No conflict errors

**Test Case 4.2 - Configuration Display**:
```bash
hlpr summarize document test.pdf --verbose
```

**Expected Results**:
- Shows active configuration in Rich table
- Indicates source of each setting (config file vs CLI)
- Clear distinction between defaults and overrides

### Scenario 5: Output Formatting

**Test Case 5.1 - Rich Terminal Output**:
```bash
hlpr summarize document test.pdf --format rich
```

**Expected Results**:
- Beautiful Rich panels for summary and key points
- Color-coded sections
- Proper text wrapping and formatting
- Metadata displayed in organized table

**Test Case 5.2 - JSON Output Piping**:
```bash
hlpr summarize document test.pdf --format json | jq '.results[0].summary'
```

**Expected Results**:
- Valid JSON output suitable for piping
- No Rich formatting in piped output
- Extractable fields via jq or similar tools

**Test Case 5.3 - File Output**:
```bash
hlpr summarize document test.pdf --save --output my_summary.md --format md
```

**Expected Results**:
- Creates markdown file with proper formatting
- Confirmation message with file location
- File contains all summary data
- Proper markdown syntax

## Performance Validation

### Startup Time Test
```bash
time hlpr summarize document small_file.txt --format json
```
**Target**: Complete in < 2 seconds for small files

### Large File Test
```bash
hlpr summarize document large_document.pdf --verbose
```
**Target**: Shows progress for files > 10MB, completes without memory issues

### Batch Processing Test
```bash
time hlpr summarize document *.pdf --batch --format json
```
**Target**: Processes multiple files efficiently, shows per-file progress

## Accessibility Validation

### Keyboard Navigation
- All guided mode interactions accessible via keyboard only
- Tab navigation where applicable
- Clear keyboard shortcuts displayed

### Screen Reader Compatibility
- Rich output should degrade gracefully for screen readers
- Alternative text representations available
- No essential information conveyed by color alone

### Terminal Compatibility  
- Works in various terminal emulators
- Handles different terminal sizes gracefully
- Fallback for terminals without Rich support

## Success Criteria

### Functional Requirements Met
- ✅ FR-001: Guided interactive mode implemented
- ✅ FR-002: Real-time progress indicators using Rich
- ✅ FR-003: Rich panels for summary presentation
- ✅ FR-004: Contextual help and error guidance
- ✅ FR-005: Direct command execution supported
- ✅ FR-006: Batch processing capability
- ✅ FR-007: Verbose mode implementation
- ✅ FR-008: Output redirection support

### User Experience Validation
- New users can successfully complete guided mode without help
- Power users can execute commands efficiently
- Error messages lead to successful resolution
- Progress feedback provides meaningful information

### Technical Validation
- No memory leaks during large file processing
- Graceful handling of interruptions
- Proper cleanup of temporary resources
- Integration with existing hlpr architecture

## Troubleshooting Common Issues

### Rich Output Not Displaying
**Symptom**: Plain text output instead of formatted panels
**Solution**: Check terminal compatibility, try `--format txt` as fallback

### Progress Bar Not Updating
**Symptom**: Static progress display
**Solution**: Check terminal size, verify Rich compatibility

### Batch Processing Failures
**Symptom**: Processing stops after first error
**Solution**: Verify `--batch` flag is used, check file permissions

### Performance Issues
**Symptom**: Slow startup or processing
**Solution**: Use `--verbose` to identify bottlenecks, check provider availability

## Next Steps

After validating all scenarios:
1. Document any discovered issues or improvements
2. Update configuration examples based on real usage
3. Create user documentation with screenshots
4. Consider additional interactive features based on user feedback

This quickstart serves as both validation criteria and user onboarding guide for the enhanced CLI/TUI experience.