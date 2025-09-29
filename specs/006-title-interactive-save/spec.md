# Feature Specification: Interactive save prompt (Rich)

**Feature Branch**: `006-title-interactive-save`  
**Created**: 2025-09-29  
**Status**: Draft  
**Input**: User description: "Add interactive 'save summary' prompts using rich.prompt when --save is not provided: confirm save (default yes), choose format (md/txt/json default md), destination path default to existing default output path, use atomic_write_text from hlpr.io.atomic, include JSON save option with generated_at timestamp, auto-save defaults when non-interactive, and add unit tests and docs."

## Execution Flow (main)
```
1. Parse user description from Input
   → If empty: ERROR "No feature description provided"
2. Extract key concepts from description
   → Identify: actors, actions, data, constraints
3. For each unclear aspect:
   → Mark with [NEEDS CLARIFICATION: specific question]
4. Fill User Scenarios & Testing section
   → If no clear user flow: ERROR "Cannot determine user scenarios"
5. Generate Functional Requirements
   → Each requirement must be testable
   → Mark ambiguous requirements
6. Identify Key Entities (if data involved)
7. Run Review Checklist
   → If any [NEEDS CLARIFICATION]: WARN "Spec has uncertainties"
   → If implementation details found: ERROR "Remove tech details"
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

### Section Requirements
- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation
When creating this spec from a user prompt:
1. **Mark all ambiguities**: Use [NEEDS CLARIFICATION: specific question] for any assumption you'd need to make
2. **Don't guess**: If the prompt doesn't specify something (e.g., "login system" without auth method), mark it
3. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item
4. **Common underspecified areas**:
   - User types and permissions
   - Data retention/deletion policies  
   - Performance targets and scale
   - Error handling behaviors
   - Integration requirements
   - Security/compliance needs

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
As a user who runs `hlpr summarize document <file>` interactively (no `--save` flag), I want to be prompted after the summary is displayed to save the summary so I can choose whether to persist it, pick the format, and select the destination path using sensible defaults.

### Acceptance Scenarios
1. **Given** an interactive terminal and no `--save` flag, **When** the summary is displayed, **Then** the CLI prompts: "Would you like to save the summary? (yes/no) [Y]: " with default Yes. If the user accepts (presses Enter or types yes), the CLI then prompts for format (md/txt/json) with default `md`, then prompts for destination path with a sensible default (existing default output path), and finally saves the file atomically and prints the saved path.
2. **Given** an interactive terminal and the user responds `no` to the save prompt, **When** the user declines, **Then** the CLI prints a short message (e.g., "Summary not saved.") and exits without writing a file.
3. **Given** a non-interactive environment (stdin not a TTY) and no `--save` flag, **When** the command runs, **Then** the CLI does not prompt and does not save (privacy-first). To enable auto-save in non-interactive contexts, use `--save` flag or set `HLPR_AUTO_SAVE=true` environment variable.
4. **Given** the user selects `json` format, **When** the save is performed, **Then** the saved JSON file contains at least `summary` and `generated_at` (ISO8601) fields and is written atomically.

### Edge Cases
- User provides invalid format input (e.g., "markdwn"): CLI reprompts and shows supported choices.
- Destination directory does not exist: CLI attempts to create directories (mkdir -p). If creation fails due to permissions, the CLI prints an error and does not crash.
- File already exists: CLI will avoid overwriting by appending a timestamp suffix to the filename (e.g., `_20250929T153000`) to preserve the existing file and produce a unique output path.
- Non-interactive environment but output path points to read-only filesystem: CLI should raise a StorageError with helpful details.
- When atomic write helper fails at OS-level, fallback to a best-effort write should be attempted, but an error will be surfaced if that also fails.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: When `hlpr summarize document` or `hlpr summarize meeting` is run without `--save`, the CLI MUST prompt the user to confirm whether they want to save the summary, using Rich's prompt module (`rich.prompt.Confirm`) with default Yes.
- **FR-002**: If the user confirms, the CLI MUST prompt for the save format using `rich.prompt.Prompt` with choices [`md`, `txt`, `json`] and default `md`. The input must be validated and the prompt repeated on invalid input.
- **FR-003**: If the user confirms, the CLI MUST prompt for a destination path using `rich.prompt.Prompt` with default set to the organized storage path from `prefs.to_organized_storage().get_organized_path(document.path, format)` (fallback to `_determine_output_path` if organized storage not configured). If the directory does not exist, the CLI MUST attempt to create it.
- **FR-004**: The CLI MUST use `hlpr.io.atomic.atomic_write_text` to persist the file atomically. If JSON format is chosen, the CLI MUST include a `generated_at` ISO8601 timestamp alongside the `summary` field.
- **FR-005**: In non-interactive contexts (stdin is not a TTY), the CLI MUST not block on prompts. Auto-save is opt-in only via explicit `--save` flag or `HLPR_AUTO_SAVE=true` environment variable to preserve privacy-first design. This behavior must be documented and testable.
- **FR-006**: All errors during saving (permission errors, disk space) MUST be surfaced as `StorageError` with helpful details; the CLI should print a user-friendly error message and exit with an appropriate exit code.

*Clarifications / optional behavior*:
- **FR-007**: When the computed destination file already exists, the CLI MUST avoid overwriting by appending a timestamp suffix to the filename (format `_YYYYMMDDTHHMMSS`, e.g. `_20250929T153000`) to produce a unique output path. This ensures previously saved summaries are preserved by default.

## Clarifications

### Session 2025-09-29

- Q: When the destination file already exists, which behavior should the CLI use? → A: C (avoid overwriting by appending timestamp suffix to filename)

*Example of marking unclear requirements:*
- **FR-006**: System MUST authenticate users via [NEEDS CLARIFICATION: auth method not specified - email/password, SSO, OAuth?]
- **FR-007**: System MUST retain user data for [NEEDS CLARIFICATION: retention period not specified]

### Key Entities *(include if feature involves data)*
- **SavedSummary**: Represents a summary saved to disk with attributes: path (filesystem location), format (md/txt/json), generated_at (ISO8601 timestamp), summary (text content), source_file (original document name)

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [ ] Focused on user value and why this prompt exists
- [ ] Minimal implementation detail but references to Rich prompt module are acceptable because this spec intentionally guides UI behavior
- [ ] All mandatory sections completed

### Requirement Completeness
- [ ] No unresolved [NEEDS CLARIFICATION] markers other than overwrite confirmation
- [ ] Requirements are testable and unambiguous
- [ ] Success criteria are measurable (file existence, content, default behaviors)
- [ ] Scope is clearly bounded to CLI prompt and save flow; it does not change existing organized storage semantics beyond using Rich prompts
- [ ] Dependencies and assumptions identified (uses existing `atomic_write_text`, relies on `sys.stdin.isatty()` for TTY detection)

---

## Execution Status
*Updated by script run on 2025-09-29*

- [x] User description parsed
- [x] Key concepts extracted (interactive prompt, format choices, atomic write, non-interactive defaults)
- [x] Ambiguities marked (overwrite confirmation)
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [ ] Review checklist pending author review

---
