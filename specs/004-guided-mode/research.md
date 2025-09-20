# Research: Guided Workflow Implementation Approach

**Feature**: Robust Guided Workflow for Document Summarization  
**Phase**: 0 - Outline & Research  
**Date**: September 20, 2025

## Research Tasks Completed

### 1. Existing CLI Interactive Patterns Analysis

**Current State Analysis:**
- `src/hlpr/cli/interactive.py` contains simulation-only guided mode
- Rich display infrastructure established in `src/hlpr/cli/rich_display.py`
- Progress tracking implemented via `PhaseTracker` and `ProgressTracker`
- Error handling patterns standardized with Rich panels

**Key Findings:**
- `InteractiveSession` class already exists with phase-based workflow
- `_simulate_phases()` method provides structure to enhance
- Rich prompts and panels already imported and available
- Progress infrastructure supports real processing integration

### 2. Current Guided Mode Implementation Review

**Reuse Opportunities Identified:**
- Phase-based workflow structure (parsing → chunking → summarization)
- Rich display patterns for progress bars and result panels
- Error handling infrastructure with actionable messages
- CLI argument parsing and validation patterns

**Enhancement Points:**
- Replace simulation with real CLI function calls
- Add interactive option collection before processing
- Integrate command template generation after results
- Maintain existing progress display aesthetics

### 3. Rich Display Patterns for Option Collection

**Available Rich Components:**
- `Prompt.ask()` for simple input with defaults
- `Confirm.ask()` for yes/no questions
- `IntPrompt.ask()` for numeric inputs with validation
- `Panel` for grouped option displays
- `Console.print()` with markup for styled prompts

**UX Patterns to Implement:**
- Two-tier option collection (basic → advanced on request)
- Default value display in prompts: `[default: local]`
- Validation with retry on invalid input
- Clear section separation with Rich panels

### 4. Command Template Generation Best Practices

**Template Format Research:**
- Use placeholder format: `[PASTE FILE PATH HERE]`
- Include all selected options as CLI flags
- Show both short and long flag formats where available
- Add explanatory comments for complex options

**Storage Strategy:**
- JSON format for structured command history
- ~/.hlpr/ directory for user-specific data
- Atomic writes to prevent corruption
- Metadata tracking (usage count, creation date)

## Implementation Decisions

### Decision: Enhance Existing InteractiveSession Class
**Rationale:** 
- Maintains consistency with established architecture
- Leverages existing Rich infrastructure and error handling
- Preserves user familiarity with current guided mode interface
- Minimizes code duplication and testing overhead

**Alternatives Considered:**
- **New Module Approach**: Creating separate guided workflow module
  - Rejected: Would duplicate existing Rich display and progress patterns
- **Command Line Wizard**: Step-by-step command builder
  - Rejected: Less intuitive than integrated processing workflow

### Decision: Reuse Existing CLI Helper Functions
**Rationale:**
- `_parse_with_progress()` already handles document parsing with Rich display
- `_summarize_with_progress()` provides complete summarization pipeline
- `_display_summary()` handles all output formats correctly
- Error handling and recovery already implemented

**Alternatives Considered:**
- **Direct API Calls**: Bypassing CLI helpers for core functions
  - Rejected: Would lose Rich progress display and error handling
- **Duplicate Logic**: Reimplementing parsing and summarization
  - Rejected: Violates DRY principle and increases maintenance burden

### Decision: Pydantic Models for Option Validation
**Rationale:**
- Type safety for interactive option collection
- Built-in validation with clear error messages
- Integration with existing configuration patterns
- Support for default values and constraints

**Implementation Approach:**
```python
class ProcessingOptions(BaseModel):
    provider: str = "local"
    format: str = "rich" 
    temperature: float = Field(0.3, ge=0.0, le=1.0)
    chunk_size: int = Field(8192, gt=0)
    # ... other options
```

### Decision: Command Template JSON Storage
**Rationale:**
- Structured data for metadata tracking
- Easy parsing and modification
- Supports future features (categories, favorites)
- Atomic write operations for data safety

**Schema Design:**
```json
{
  "commands": [
    {
      "id": "cmd_001",
      "template": "hlpr summarize document {file} --provider {provider}",
      "options": {"provider": "local", "format": "rich"},
      "created": "2025-09-20T10:30:00Z",
      "usage_count": 0
    }
  ]
}
```

## Technical Implementation Notes

### Integration Points Identified
1. **Option Collection → CLI Arguments**: Convert interactive choices to CLI argument format
2. **Progress Display → Real Processing**: Replace simulation with actual function calls
3. **Results Display → Template Generation**: Extract used options for command templates
4. **Error Handling → User Recovery**: Provide retry and help options

### Risk Mitigation
- **Backward Compatibility**: Existing `hlpr summarize guided` command unchanged in interface
- **Error Recovery**: All interactive prompts allow retry on invalid input
- **Graceful Degradation**: Fallback to defaults if interaction fails
- **Testing Strategy**: Contract tests for each functional requirement

### Performance Considerations
- Interactive prompts cached to avoid re-prompting on navigation
- Command template generation is O(1) operation
- Rich display operations optimized for terminal responsiveness
- File I/O operations use existing atomic write patterns

---

**Research Status**: ✅ Complete  
**Next Phase**: Phase 1 - Design & Contracts  
**Confidence Level**: High - Clear implementation path with minimal risk