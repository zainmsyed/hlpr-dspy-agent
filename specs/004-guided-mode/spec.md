# Feature Specification: Robust Guided Workflow for Document Summarization

**Feature Branch**: `004-guided-mode`  
**Created**: September 20, 2025  
**Status**: Draft  
**Input**: User description: "guided-mode"

## Execution Flow (main)
```
1. Parse user description from Input
   → Parsed: Transform simulation-only guided mode into fully functional interactive experience
2. Extract key concepts from description
   → Actors: CLI users wanting document summarization guidance
   → Actions: Interactive option collection, real document processing, command generation
   → Data: Document files, user preferences, processing results, saved command templates
   → Constraints: Must reuse existing CLI functions, maintain backward compatibility
3. For each unclear aspect:
   → All aspects clearly defined in PRD
4. Fill User Scenarios & Testing section
   → User flow: guided option collection → document processing → results display → command template
5. Generate Functional Requirements
   → All requirements testable and measurable
6. Identify Key Entities
   → Documents, processing options, command templates, progress phases
7. Run Review Checklist
   → No clarifications needed, ready for planning
8. Return: SUCCESS (spec ready for planning)
```

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
A user wants to summarize a document but isn't familiar with all available CLI options. They run `hlpr summarize guided` and are guided through an interactive workflow that:
1. Collects their preferences through simple prompts with sensible defaults
2. Processes their document with real-time progress feedback
3. Displays results in their chosen format
4. Provides a reusable command template for future use

### Acceptance Scenarios
1. **Given** a user runs `hlpr summarize guided`, **When** they accept all defaults by pressing Enter, **Then** the system processes the document using local provider with rich output format
2. **Given** a user selects advanced options, **When** they configure temperature and chunk size, **Then** the system applies these settings during processing
3. **Given** a user chooses to save output, **When** processing completes, **Then** the system saves results to their specified file path using atomic writes
4. **Given** processing completes successfully, **When** the system generates a command template, **Then** the template contains the exact options used with a file path placeholder
5. **Given** a user presses Ctrl+C during guided mode, **When** they confirm exit, **Then** the system exits gracefully without corrupting any data

### Edge Cases
- What happens when user enters invalid provider choice? → Re-prompt with error message and available options
- How does system handle file processing errors? → Use existing CLI error panels and allow retry
- What if user saves command template but storage fails? → Show warning but continue, don't block workflow
- How does system behave with very large documents? → Use existing chunking and progress display

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST provide interactive guided mode accessible via `hlpr summarize guided` command
- **FR-002**: System MUST collect user preferences through two-tier option system (basic and advanced)
- **FR-003**: System MUST provide sensible defaults for all options that users can accept by pressing Enter
- **FR-004**: System MUST process documents using the same pipeline as direct CLI commands
- **FR-005**: System MUST display real-time progress through parsing, chunking, and summarization phases
- **FR-006**: System MUST support all existing output formats (rich, txt, md, json)
- **FR-007**: System MUST generate equivalent CLI command templates with file path placeholders
- **FR-008**: System MUST handle invalid user input by re-prompting with clear error messages
- **FR-009**: System MUST support graceful exit on keyboard interrupts with confirmation
- **FR-010**: System MUST reuse existing CLI functions for parsing, processing, and display
- **FR-011**: System MUST save results to files using atomic write operations when requested
- **FR-012**: System MUST support basic options: provider, format, save-to-file, output-path
- **FR-013**: System MUST support advanced options: model, temperature, chunk-size, chunk-overlap, chunking-strategy, verify-hallucinations

### Key Entities *(include if feature involves data)*
- **InteractiveSession**: Manages guided workflow state and user interactions
- **ProcessingOptions**: Encapsulates user-selected configuration (provider, format, temperature, etc.)
- **CommandTemplate**: Represents reusable CLI command with placeholders
- **ProgressPhase**: Tracks current processing stage (parsing, chunking, summarizing)
- **SavedCommand**: Persisted command template with metadata for reuse

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous  
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---
