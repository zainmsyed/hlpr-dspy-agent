# Contract Test Specifications

**Purpose**: Define failing test cases that validate functional requirements  
**Location**: Tests to be created in `/tests/contract/`

## Test File: test_cli_guided_enhanced.py

### End-to-End Guided Workflow Tests

```python
import pytest
from hlpr.cli.interactive import InteractiveSession
from hlpr.models.interactive import ProcessingOptions

class TestGuidedWorkflowComplete:
    """Test complete guided workflow end-to-end (FR-001, FR-004, FR-010)."""
    
    def test_guided_mode_with_defaults(self, temp_document):
        """
        Test: User accepts all defaults through guided workflow
        
        Given: User runs guided mode with a document
        When: User presses Enter for all prompts (accepts defaults)
        Then: Document is processed with local provider and rich format
        And: Results are displayed correctly
        And: Command template is generated
        
        Validates: FR-001, FR-003, FR-004, FR-005, FR-006, FR-007
        """
        # This test will FAIL until implementation complete
        session = InteractiveSession()
        
        # Mock user input: all defaults (Enter key)
        with patch('rich.prompt.Prompt.ask') as mock_prompt:
            mock_prompt.side_effect = ["local", "rich", "no"]  # Provider, format, save
            
            result = session.run_guided_workflow(temp_document)
            
        assert result.success is True
        assert result.provider == "local"
        assert result.format == "rich"
        assert result.template is not None
        assert "[PASTE FILE PATH HERE]" in result.template.command_template
        
    def test_guided_mode_with_advanced_options(self, temp_document):
        """
        Test: User configures advanced options
        
        Given: User runs guided mode
        When: User requests advanced options and configures temperature and chunk size
        Then: Document is processed with custom settings
        And: Template includes advanced settings
        
        Validates: FR-002, FR-013
        """
        # This test will FAIL until implementation complete
        session = InteractiveSession()
        
        with patch('rich.prompt.Prompt.ask') as mock_prompt:
            # Basic: local, rich, no save, yes advanced
            # Advanced: default model, 0.7 temp, 4096 chunk, defaults for rest
            mock_prompt.side_effect = [
                "local", "rich", "no", "yes",  # Basic + advanced request
                "gemma3:latest", "0.7", "4096", "256", "sentence", "no"  # Advanced
            ]
            
            result = session.run_guided_workflow(temp_document)
            
        assert result.options.temperature == 0.7
        assert result.options.chunk_size == 4096
        assert "--temperature 0.7" in result.template.command_template
        assert "--chunk-size 4096" in result.template.command_template
```

### Option Collection Tests

```python
class TestInteractiveOptionCollection:
    """Test interactive option collection methods (FR-002, FR-008)."""
    
    def test_basic_options_collection_valid_input(self):
        """
        Test: Valid input for basic options
        
        Given: Interactive session ready for option collection
        When: User provides valid choices for all basic options
        Then: ProcessingOptions object created with correct values
        
        Validates: FR-002, FR-012
        """
        # This test will FAIL until implementation complete
        session = InteractiveSession()
        
        with patch('rich.prompt.Prompt.ask') as mock_prompt:
            mock_prompt.side_effect = ["openai", "md", "yes", "/tmp/output.md"]
            
            options = session.collect_basic_options()
            
        assert options.provider == "openai"
        assert options.format == "md"
        assert options.save_to_file is True
        assert options.output_path == "/tmp/output.md"
        
    def test_basic_options_invalid_input_retry(self):
        """
        Test: Invalid input causes re-prompt with error message
        
        Given: Interactive session collecting options
        When: User enters invalid provider then valid one
        Then: System re-prompts with error message and succeeds
        
        Validates: FR-008
        """
        # This test will FAIL until implementation complete
        session = InteractiveSession()
        
        with patch('rich.prompt.Prompt.ask') as mock_prompt:
            mock_prompt.side_effect = ["invalid", "local", "rich", "no"]  # Invalid then valid
            
            options = session.collect_basic_options()
            
        # Should have re-prompted after invalid input
        assert mock_prompt.call_count >= 2  # Re-prompt occurred
        assert options.provider == "local"  # Final valid input
        
    def test_advanced_options_collection(self):
        """
        Test: Advanced options collection with validation
        
        Given: Basic options already collected
        When: User requests advanced options and provides valid values
        Then: Advanced options added to ProcessingOptions
        
        Validates: FR-013
        """
        # This test will FAIL until implementation complete
        base_options = ProcessingOptions(provider="local", format="rich")
        session = InteractiveSession()
        
        with patch_advanced_prompts() as prompts:
            prompts.side_effect = ["gpt-4", "0.8", "16384", "512", "paragraph", "yes"]
            
            enhanced_options = session.collect_advanced_options(base_options)
            
        assert enhanced_options.model == "gpt-4"
        assert enhanced_options.temperature == 0.8
        assert enhanced_options.chunk_size == 16384
        assert enhanced_options.verify_hallucinations is True
```

### Progress Display Tests

```python
class TestProgressIntegration:
    """Test progress display during real processing (FR-005)."""
    
    def test_progress_display_phases(self, temp_document):
        """
        Test: Progress shown through parsing, chunking, summarization
        
        Given: Document ready for processing
        When: Guided workflow processes the document
        Then: Progress bars shown for each phase
        And: Phase names displayed correctly
        
        Validates: FR-005
        """
        # This test will FAIL until implementation complete
        session = InteractiveSession()
        options = ProcessingOptions(provider="local", format="rich")
        
        with patch_progress_tracker() as tracker:
            result = session.process_document_with_options(temp_document, options)
            
        # Verify progress phases were called
        tracker.start_phase.assert_any_call("Parsing document")
        tracker.start_phase.assert_any_call("Chunking content") 
        tracker.start_phase.assert_any_call("Summarizing with local provider")
        assert result.success is True
```

### Command Template Tests

```python
class TestCommandTemplateGeneration:
    """Test command template generation and display (FR-007)."""
    
    def test_template_generation_basic_options(self):
        """
        Test: Template generated from basic options
        
        Given: ProcessingOptions with basic settings
        When: generate_command_template called
        Then: Template contains correct CLI arguments
        And: File placeholder present
        
        Validates: FR-007
        """
        # This test will FAIL until implementation complete
        options = ProcessingOptions(provider="openai", format="json", temperature=0.5)
        session = InteractiveSession()
        
        template = session.generate_command_template(options)
        
        assert "[PASTE FILE PATH HERE]" in template.command_template
        assert "--provider openai" in template.command_template
        assert "--format json" in template.command_template
        assert "--temperature 0.5" in template.command_template
        assert template.id.startswith("cmd_")
        
    def test_template_generation_advanced_options(self):
        """Test template includes advanced options when set."""
        # This test will FAIL until implementation complete
        
    def test_template_display_and_save_prompt(self):
        """
        Test: Template displayed with save prompt
        
        Given: Generated command template
        When: display_command_template called
        Then: Rich panel shows formatted template
        And: User prompted to save template
        
        Validates: FR-007
        """
        # This test will FAIL until implementation complete
```

### Error Handling Tests

```python
class TestErrorHandlingAndRecovery:
    """Test error handling and graceful recovery (FR-008, FR-009)."""
    
    def test_keyboard_interrupt_handling(self):
        """
        Test: Ctrl+C handling with confirmation
        
        Given: Guided workflow in progress
        When: User presses Ctrl+C
        Then: Exit confirmation prompt shown
        And: Second Ctrl+C exits gracefully
        
        Validates: FR-009
        """
        # This test will FAIL until implementation complete
        session = InteractiveSession()
        
        with patch('signal.signal') as mock_signal:
            # Simulate keyboard interrupt during option collection
            mock_signal.side_effect = KeyboardInterrupt()
            
            exit_requested = session.handle_keyboard_interrupt()
            
        assert exit_requested is True  # Should confirm exit
        
    def test_file_processing_error_recovery(self, invalid_document):
        """
        Test: File processing errors handled gracefully
        
        Given: Document that will cause processing error
        When: Guided workflow attempts processing
        Then: Error displayed in Rich panel
        And: User given option to retry or exit
        
        Validates: FR-008
        """
        # This test will FAIL until implementation complete
        
    def test_template_save_error_handling(self):
        """Test template save failures handled gracefully."""
        # This test will FAIL until implementation complete
```

## Test File: test_cli_interactive_options.py

### Input Validation Tests

```python
class TestOptionValidation:
    """Test Pydantic validation of ProcessingOptions."""
    
    def test_temperature_range_validation(self):
        """Test temperature must be 0.0-1.0."""
        # This test will FAIL until implementation complete
        
        with pytest.raises(ValidationError):
            ProcessingOptions(temperature=1.5)  # Too high
            
        with pytest.raises(ValidationError):
            ProcessingOptions(temperature=-0.1)  # Too low
            
        # Valid values should work
        options = ProcessingOptions(temperature=0.0)
        assert options.temperature == 0.0
        
        options = ProcessingOptions(temperature=1.0)
        assert options.temperature == 1.0
        
    def test_chunk_size_validation(self):
        """Test chunk size must be positive integer."""
        # This test will FAIL until implementation complete
        
    def test_provider_validation(self):
        """Test provider must be in supported list."""
        # This test will FAIL until implementation complete
        
    def test_save_to_file_requires_path(self):
        """Test output_path required when save_to_file is True."""
        # This test will FAIL until implementation complete
```

## Expected Test Results

**Current State**: All tests should FAIL  
**Reason**: Implementation not yet created  
**Success Criteria**: Tests pass after implementation complete

### Test Execution Command
```bash
# Run contract tests (should fail initially)
uv run pytest -v tests/contract/test_cli_guided_enhanced.py tests/contract/test_cli_interactive_options.py
```

### Test Coverage Requirements
- [ ] FR-001: Interactive guided mode command
- [ ] FR-002: Two-tier option collection
- [ ] FR-003: Default value acceptance  
- [ ] FR-004: Document processing pipeline reuse
- [ ] FR-005: Real-time progress display
- [ ] FR-006: Output format support
- [ ] FR-007: Command template generation
- [ ] FR-008: Input validation and error handling
- [ ] FR-009: Graceful exit on interrupts
- [ ] FR-010: CLI function reuse
- [ ] FR-011: Atomic file operations
- [ ] FR-012: Basic option support
- [ ] FR-013: Advanced option support

---

**Contract Test Status**: ✅ Defined  
**Implementation Status**: ❌ Not Started (tests will fail)  
**Next Phase**: Task generation to implement these contracts