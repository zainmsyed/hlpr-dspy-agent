# Feature Specification: hlpr — Personal AI Assistant (CLI + FastAPI)

**Feature Branch**: `001-hlpr-ai-assistant`  
**Created**: 2025-09-09  
**Status**: Draft  
**Input**: User description: "Personal AI assistant designed as a modular CLI application with optional FastAPI backend for summarizing documents, meeting notes, and emails with local LLM support"

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
As a knowledge worker managing personal documents, meeting notes, and email overload, I want a privacy-centric AI assistant that I can run locally via CLI or API so that I can quickly understand and act upon my information while keeping sensitive data on my machine.

### Acceptance Scenarios
1. **Given** I have a PDF document on my computer, **When** I run `hlpr summarize doc --file report.pdf`, **Then** the CLI displays a concise summary with key points and offers to save it as MD/TXT.

2. **Given** I have meeting notes in a text file, **When** I run `hlpr summarize meeting --file notes.txt`, **Then** the CLI returns a structured summary with Overview, Key Points, Action Items, and extracts participant names if present.

3. **Given** I have configured my Gmail account with app password, **When** I run `hlpr email process --account gmail --mailbox INBOX --filter unread`, **Then** the system fetches emails securely, classifies them by category (Important, Work, Personal, etc.), and provides summaries.

4. **Given** I have Ollama running locally on localhost:11434, **When** I configure hlpr to use the local endpoint, **Then** all AI processing happens locally without sending data to cloud providers.

5. **Given** I want to use the system programmatically, **When** I start the FastAPI server and POST to `/summarize/document`, **Then** I receive structured JSON responses for integration with other tools.

### Edge Cases
- If a PDF is scanned (image-only), CLI shows error that document can't be summarized because it's an image
- Very large documents (>10k tokens): CLI chunks input and summarizes progressively using best practices for chunking strategy
- Email authentication failures: CLI surfaces clear error and doesn't store invalid credentials  
- Network failures to local LLM endpoint: CLI provides helpful error and aborts, telling user why the process failed
- Unsupported file formats: CLI validates input files and returns clear errors for unsupported formats

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: CLI MUST provide a `summarize document` command that accepts PDF, DOCX, TXT, and MD files and returns concise summaries with optional saved output (MD/TXT format).

- **FR-002**: CLI MUST provide a `summarize meeting` command that accepts meeting notes/transcript text and returns structured sections: Overview, Key Points, Action Items, and Participants (if mentioned).

- **FR-003**: System MUST provide email processing capabilities that connect to IMAP/IMAPS servers (Gmail, Outlook, custom), fetch messages with filtering (unread, date range, sender), and classify emails into categories (Important, Promotional, Newsletter, Work, Personal, Spam, Action Required).

- **FR-004**: System MUST support both local LLM endpoints via HTTP (default: http://localhost:11434 for Ollama) and cloud LLM providers (OpenAI, Anthropic) with runtime selection capability.

- **FR-005**: CLI MUST present Rich-formatted output including tables, syntax-highlighted snippets, progress bars, and color-coded summaries, plus an interactive guided mode for common tasks.

- **FR-006**: System MUST store email credentials and cloud API keys securely using the system keyring service, with CLI commands to add/update/remove account configurations.

- **FR-007**: FastAPI backend MUST expose REST endpoints for core functionality: /summarize/document, /summarize/meeting, /email/process, /email/accounts with API key protection when exposed beyond localhost.

- **FR-008**: System MUST validate input files and return clear error messages for unsupported formats or unreadable files.

- **FR-009**: System MUST handle large inputs by chunking to stay within model context windows using best practice aggregation strategies for summaries.

- **FR-010**: System MUST integrate DSPy framework for AI pipelines and MIPRO optimization to automatically refine prompts for summarization and classification tasks.

- **FR-011**: System MUST support both guided mode for beginners and power mode for experienced users with direct command execution.

- **FR-012**: Email processing MUST enforce TLS/SSL connections, support username/password authentication (app passwords for Gmail/Outlook), and be read-only (no sending/replying in v1).

### Key Entities *(include if feature involves data)*
- **Document**: Represents files for processing. Attributes: path, type (PDF/DOCX/TXT/MD), size, extracted content, summary.
- **MeetingNote**: Meeting content for analysis. Attributes: text content, participants list, date, structured summary sections.
- **EmailAccount**: IMAP configuration. Attributes: provider, host, port, username, secure credential reference, default mailbox.
- **EmailMessage**: Processed email data. Attributes: message_id, sender, recipients, subject, date, body, classification category, summary.
- **AIProvider**: LLM configuration. Attributes: type (local/cloud), endpoint URL, model name, authentication method.

### Non-Functional Requirements
- **Privacy**: Default preference for local processing with clear data flow communication
- **Performance**: Efficient file parsing, optimized prompts via MIPRO, responsive CLI, graceful large file handling
- **Security**: Secure credential storage, TLS enforcement for email, API key protection
- **Modularity**: Clear separation between CLI, AI core, file processors, LLM adapters, email client, API layer
- **Usability**: Intuitive for beginners, efficient for power users, helpful error messages

---


## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [x] No implementation details that are irrelevant to stakeholders (core non-functional notes allowed)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] Ambiguities are either resolved or marked with [NEEDS CLARIFICATION]
- [x] Requirements are testable and unambiguous where possible
- [x] Success criteria are measurable (see acceptance scenarios)
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
