# Quickstart: Guided Workflow Implementation

**Feature**: Robust Guided Workflow for Document Summarization  
**Version**: 1.0  
**Date**: September 20, 2025

This quickstart validates the guided workflow implementation through step-by-step testing and usage scenarios.

## Prerequisites

### Development Environment
```bash
# Ensure you're in the feature branch
git checkout 004-guided-mode

# Install development dependencies (if needed)
uv add --dev pytest pytest-mock

# Verify existing CLI infrastructure
uv run python -m src.hlpr.cli check-setup
```

### Test Documents
```bash
# Create test documents for validation
mkdir -p /tmp/hlpr-test-docs

cat > /tmp/hlpr-test-docs/sample.md << 'EOF'
# Sample Document

This is a test document for validating the guided workflow functionality.

## Key Points
- Interactive option collection
- Progress display
- Command template generation

The document contains enough content to test parsing, chunking, and summarization phases.
EOF

cat > /tmp/hlpr-test-docs/large-sample.txt << 'EOF'
This is a larger test document that will trigger chunking behavior...
[Content continues for several paragraphs to ensure chunking occurs]
EOF
```

## Implementation Validation Steps

### Step 1: Verify Contract Tests Fail (Pre-Implementation)
```bash
# These tests should FAIL before implementation
uv run pytest -v tests/contract/test_cli_guided_enhanced.py
uv run pytest -v tests/contract/test_cli_interactive_options.py

# Expected output: All tests fail with import/implementation errors
# This confirms tests are properly defined and will validate implementation
```

### Step 2: Basic Guided Workflow Test
```bash
# Test the enhanced guided mode (after implementation)
uv run hlpr summarize guided /tmp/hlpr-test-docs/sample.md

# Expected interaction flow:
# 1. "AI Provider [local|openai|anthropic|groq|together] (local): " → Press Enter
# 2. "Output Format [rich|txt|md|json] (rich): " → Press Enter
# 3. "Save to file? [y/N]: " → Press Enter
# 4. "Configure advanced options? [y/N]: " → Press Enter
# 5. Progress display: Parsing → Chunking → Summarization
# 6. Rich-formatted summary results
# 7. Command template display with save prompt
```

### Step 3: Advanced Options Test
```bash
# Test advanced options workflow
uv run hlpr summarize guided /tmp/hlpr-test-docs/sample.md

# Interaction sequence:
# 1. Basic options: local, rich, no save
# 2. Advanced options: "y"
# 3. Model: "gemma3:latest" (or custom)
# 4. Temperature: "0.7"
# 5. Chunk Size: "4096" 
# 6. Other advanced options: defaults
# 7. Verify processing uses custom settings
# 8. Verify template includes advanced options
```

### Step 4: Error Handling Validation
```bash
# Test invalid input handling
uv run hlpr summarize guided /tmp/hlpr-test-docs/sample.md

# Test sequence:
# 1. Provider prompt: enter "invalid" → should re-prompt with error
# 2. Provider prompt: enter "local" → should accept
# 3. Temperature (advanced): enter "5.0" → should re-prompt with range error
# 4. Temperature: enter "0.7" → should accept
```

### Step 5: File Output Test
```bash
# Test file saving functionality
uv run hlpr summarize guided /tmp/hlpr-test-docs/sample.md

# Interaction:
# 1. Basic options: local, md, yes (save)
# 2. Output path: "/tmp/test-summary.md"
# 3. Process and verify file created
# 4. Check file contains markdown-formatted summary

ls -la /tmp/test-summary.md
cat /tmp/test-summary.md
```

### Step 6: Command Template Validation
```bash
# Test command template generation and saving
uv run hlpr summarize guided /tmp/hlpr-test-docs/sample.md

# After processing completes:
# 1. Verify template display in Rich panel
# 2. Check placeholder: "[PASTE FILE PATH HERE]"
# 3. Save template: "y"
# 4. Verify saved to ~/.hlpr/saved_commands.json

cat ~/.hlpr/saved_commands.json | jq .
```

### Step 7: Keyboard Interrupt Handling
```bash
# Test graceful exit
uv run hlpr summarize guided /tmp/hlpr-test-docs/sample.md

# During option collection, press Ctrl+C
# Expected behavior:
# 1. First Ctrl+C: "Exit guided mode? Press Ctrl+C again or 'q' to quit..."
# 2. Second Ctrl+C: Graceful exit with no corruption
# 3. Any other key: Continue workflow
```

## Integration Testing

### Contract Test Execution (Post-Implementation)
```bash
# After implementation, all contract tests should PASS
uv run pytest -v tests/contract/test_cli_guided_enhanced.py
uv run pytest -v tests/contract/test_cli_interactive_options.py

# Expected results:
# ✅ test_guided_mode_with_defaults
# ✅ test_guided_mode_with_advanced_options  
# ✅ test_basic_options_collection_valid_input
# ✅ test_basic_options_invalid_input_retry
# ✅ test_advanced_options_collection
# ✅ test_progress_display_phases
# ✅ test_template_generation_basic_options
# ✅ test_keyboard_interrupt_handling
# (and all other defined contract tests)
```

### Integration with Existing CLI
```bash
# Verify existing commands still work
uv run hlpr summarize document /tmp/hlpr-test-docs/sample.md --provider local --format rich

# Verify guided mode doesn't break existing functionality
uv run hlpr --help
uv run hlpr summarize --help
```

## Performance Validation

### Interactive Responsiveness
```bash
# Test UI responsiveness
time uv run hlpr summarize guided /tmp/hlpr-test-docs/sample.md

# Criteria:
# - Prompts appear immediately (<100ms)
# - Input validation is instant
# - Progress updates smoothly during processing
# - Template generation is immediate
```

### Large Document Handling
```bash
# Test with larger document that requires chunking
uv run hlpr summarize guided /tmp/hlpr-test-docs/large-sample.txt

# Verify:
# - Progress display shows chunking phase
# - Chunking strategy visible in progress
# - Processing completes without timeout
# - Template includes chunking options
```

## Success Criteria Checklist

### Functional Requirements Validation
- [ ] **FR-001**: `hlpr summarize guided` command accessible and functional
- [ ] **FR-002**: Two-tier option system (basic → advanced on request)
- [ ] **FR-003**: All options have defaults, Enter key acceptance works
- [ ] **FR-004**: Uses existing CLI processing pipeline (_parse_with_progress, etc.)
- [ ] **FR-005**: Real-time progress through all phases (parsing, chunking, summarization)
- [ ] **FR-006**: All output formats supported (rich, txt, md, json)
- [ ] **FR-007**: Command templates generated with placeholders
- [ ] **FR-008**: Invalid input handled with re-prompting and clear errors
- [ ] **FR-009**: Ctrl+C handled gracefully with confirmation
- [ ] **FR-010**: Existing CLI functions reused (no duplication)
- [ ] **FR-011**: File saves use atomic operations
- [ ] **FR-012**: Basic options collected (provider, format, save, path)
- [ ] **FR-013**: Advanced options available (model, temperature, chunking, etc.)

### User Experience Validation
- [ ] Fast defaults: All prompts can be skipped with Enter
- [ ] Clear prompts: Options and defaults clearly displayed
- [ ] Error recovery: Invalid input provides helpful guidance
- [ ] Progress feedback: User sees processing progress clearly
- [ ] Template utility: Generated commands are copy-pasteable
- [ ] Graceful exit: Ctrl+C doesn't corrupt data or leave artifacts

### Technical Compliance
- [ ] No new major dependencies added
- [ ] Ruff compliance: `uvx ruff check src/hlpr/cli/`
- [ ] Type hints: All new code properly typed
- [ ] Test coverage: Contract tests pass and cover all FRs
- [ ] Constitutional compliance: Modular, CLI-first, privacy-respecting

## Troubleshooting

### Common Issues

**Guided mode not found**: 
```bash
# Check CLI registration
uv run python -c "from hlpr.cli.interactive import InteractiveSession; print('OK')"
```

**Progress not displaying**:
```bash
# Verify Rich infrastructure
uv run python -c "from rich.console import Console; Console().print('[green]Rich working[/green]')"
```

**Template save failing**:
```bash
# Check directory permissions
mkdir -p ~/.hlpr
ls -la ~/.hlpr
```

### Development Commands
```bash
# Run specific test group
uv run pytest -k "guided" -v

# Check code formatting
uvx ruff format src/hlpr/cli/
uvx ruff check src/hlpr/cli/

# Debug interactive session
uv run python -c "from hlpr.cli.interactive import InteractiveSession; s = InteractiveSession(); print(s)"
```

## Completion Verification

Once all steps pass and success criteria are met, the guided workflow implementation is complete and ready for production use. Users can leverage the enhanced interactive experience for document summarization while maintaining full access to existing CLI functionality.

---

**Quickstart Status**: ✅ Ready for Implementation Testing  
**Next Step**: Execute /tasks command to generate implementation tasks  
**Estimated Completion**: 2-3 hours of focused development