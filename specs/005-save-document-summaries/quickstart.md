# Quickstart: Organized Summary Storage Implementation

## Overview
Validate the organized folder structure feature for document summary storage. This quickstart tests the enhanced CLI behavior that automatically creates `hlpr/summaries/documents/` structure and saves summaries there by default, while respecting custom paths when specified.

## Prerequisites
- hlpr CLI installed and working
- Test documents available
- Write permissions in test directory
- Python environment with required dependencies

## Test Environment Setup

### Step 1: Create Test Directory Structure
```bash
# Create isolated test environment
mkdir -p /tmp/hlpr-test-organized-storage
cd /tmp/hlpr-test-organized-storage

# Create sample test documents
echo "This is a test document for summarization with organized storage." > test_document.txt
echo "# Meeting Notes\n\nDiscussed project timeline and deliverables." > meeting_notes.md

# Verify no existing hlpr folder
ls -la | grep hlpr  # Should show nothing
```

### Step 2: Verify Current Implementation (Baseline)
```bash
# Test current behavior without organized storage
hlpr summarize document test_document.txt --save --format txt

# Expected: Creates test_document_summary.txt in current directory
ls -la *.txt | grep summary
# Should show: test_document_summary.txt

# Clean up for organized storage test
rm -f *_summary.*
```

## Core Feature Validation

### Step 3: Test Organized Storage Creation
```bash
# Test organized storage with default behavior
hlpr summarize document test_document.txt --save

# Expected outcomes:
# 1. Creates hlpr/summaries/documents/ directory structure
# 2. Saves summary as hlpr/summaries/documents/test_document_summary.md (MD default)
# 3. Shows success message indicating organized storage

# Validate directory structure created
ls -la hlpr/summaries/documents/
# Expected: test_document_summary.md

# Validate content format (should be Markdown)
head -5 hlpr/summaries/documents/test_document_summary.md
# Expected: Markdown formatting with headers
```

### Step 4: Test Multiple Document Processing
```bash
# Process second document to same organized structure
hlpr summarize document meeting_notes.md --save --format json

# Validate both files in organized structure
ls -la hlpr/summaries/documents/
# Expected: 
# test_document_summary.md
# meeting_notes_summary.json

# Verify directory wasn't recreated (timestamps should be same)
stat hlpr/summaries/
```

### Step 5: Test Custom Output Path (Bypass Organized Structure)
```bash
# Test custom path bypasses organized structure
hlpr summarize document test_document.txt --save --output /tmp/custom_summary.txt

# Validate file created at exact custom location
ls -la /tmp/custom_summary.txt
# Expected: File exists at specified path

# Validate organized structure was NOT used for this file
ls -la hlpr/summaries/documents/ | grep -v meeting_notes | grep -v test_document
# Expected: No additional files (still just the previous two)
```

### Step 6: Test Format Selection in Organized Structure
```bash
# Test different formats in organized structure
hlpr summarize document meeting_notes.md --save --format txt
hlpr summarize document meeting_notes.md --save --format json

# Validate multiple formats for same document
ls -la hlpr/summaries/documents/meeting_notes*
# Expected:
# meeting_notes_summary.md (from step 4)
# meeting_notes_summary.txt (from this step)
# meeting_notes_summary.json (from this step - overwritten)
```

## Error Handling Validation

### Step 7: Test Permission Handling
```bash
# Create read-only directory to test permission errors
mkdir -p /tmp/readonly-test
cd /tmp/readonly-test
chmod -w .

# Test organized storage with permission issues
hlpr summarize document /tmp/hlpr-test-organized-storage/test_document.txt --save

# Expected: Clear error message about permission denied
# Should not crash, should provide helpful guidance

# Clean up
cd /tmp/hlpr-test-organized-storage
```

### Step 8: Test Invalid Custom Path
```bash
# Test invalid custom output path
hlpr summarize document test_document.txt --save --output "/invalid\0path/file.txt"

# Expected: Clear validation error message
# Should not create any files or directories
```

## Backward Compatibility Validation

### Step 9: Test Existing Workflow Preservation
```bash
# Test that existing --output behavior is identical
hlpr summarize document test_document.txt --save --output ./legacy_summary.txt

# Validate exact path used (not organized)
ls -la legacy_summary.txt
# Expected: File exists in current directory, not in organized structure

# Test without --save flag (no file creation)
hlpr summarize document test_document.txt

# Expected: Display output, no file created, no directories created
```

### Step 10: Test Overwrite Warnings
```bash
# Test overwrite warning in organized structure
hlpr summarize document test_document.txt --save

# Expected: Warning about overwriting existing file
# Should show path: hlpr/summaries/documents/test_document_summary.md

# Test overwrite warning with custom path
hlpr summarize document test_document.txt --save --output legacy_summary.txt

# Expected: Warning about overwriting legacy_summary.txt
```

## Performance & Integration Testing

### Step 11: Test Batch Processing Behavior
```bash
# Create multiple test documents
for i in {1..5}; do
    echo "Test document $i content for summarization testing." > "batch_doc_$i.txt"
done

# Process multiple documents (simulated batch)
for doc in batch_doc_*.txt; do
    hlpr summarize document "$doc" --save --format md
done

# Validate all summaries in organized structure
ls -la hlpr/summaries/documents/batch_doc_*
# Expected: 5 summary files in organized structure

# Verify directory performance (should handle multiple files)
time ls hlpr/summaries/documents/
# Expected: Fast listing, no performance degradation
```

### Step 12: Test Cross-Platform Path Handling
```bash
# Test path resolution with different input paths
hlpr summarize document ./test_document.txt --save  # Relative path
hlpr summarize document /tmp/hlpr-test-organized-storage/test_document.txt --save  # Absolute path

# Both should create organized structure relative to CWD
# Both should generate same filename: test_document_summary.md
```

## Acceptance Criteria Validation

### Final Validation Checklist
- [ ] **FR-001**: `hlpr/summaries/documents/` created automatically ✓
- [ ] **FR-002**: Summaries saved to organized folder by default ✓
- [ ] **FR-003**: Filename patterns preserved ✓
- [ ] **FR-004**: Custom paths bypass organized structure ✓
- [ ] **FR-005**: Graceful error handling for permissions ✓
- [ ] **FR-006**: Overwrite warnings maintained ✓
- [ ] **FR-007**: All formats supported in organized structure ✓
- [ ] **FR-008**: Default format changed to MD ✓

### Expected Directory Structure After All Tests
```
/tmp/hlpr-test-organized-storage/
├── hlpr/
│   └── summaries/
│       └── documents/
│           ├── test_document_summary.md
│           ├── meeting_notes_summary.txt
│           ├── meeting_notes_summary.json (overwritten)
│           ├── batch_doc_1_summary.md
│           ├── batch_doc_2_summary.md
│           ├── batch_doc_3_summary.md
│           ├── batch_doc_4_summary.md
│           └── batch_doc_5_summary.md
├── legacy_summary.txt (custom path)
├── test_document.txt
├── meeting_notes.md
└── batch_doc_*.txt (original files)

/tmp/custom_summary.txt (custom path from step 5)
```

## Cleanup
```bash
# Clean up test environment
cd /tmp
rm -rf hlpr-test-organized-storage
rm -f custom_summary.txt
rm -rf readonly-test
```

## Success Criteria
1. All organized storage features work as specified
2. Backward compatibility maintained completely
3. Error handling provides clear, actionable messages
4. Performance remains acceptable for multiple files
5. Cross-platform path handling works correctly
6. No regressions in existing functionality

## Troubleshooting Guide

### Common Issues
- **Permission Denied**: Check directory write permissions
- **Path Not Found**: Verify working directory and file paths
- **Format Issues**: Ensure format parameter matches expected values
- **Overwrite Conflicts**: Review file timestamps and overwrite warnings

### Debug Commands
```bash
# Check directory permissions
ls -la hlpr/summaries/
stat hlpr/summaries/documents/

# Verify file contents and formats
file hlpr/summaries/documents/*.md
head -5 hlpr/summaries/documents/*.md
```

*Quickstart complete: Comprehensive validation of organized storage functionality*