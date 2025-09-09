# Data Model: hlpr AI Assistant

## Core Entities

### Document
Represents a file for processing and summarization.

**Fields**:
- `id`: UUID - Unique identifier
- `path`: string - Absolute file path
- `type`: enum - FILE_TYPE (PDF, DOCX, TXT, MD)
- `size_bytes`: integer - File size for chunking decisions
- `content_hash`: string - SHA256 hash for caching
- `extracted_text`: string - Raw extracted text content
- `summary`: string - Generated summary
- `created_at`: datetime - Processing timestamp
- `updated_at`: datetime - Last modification

**Validation Rules**:
- Path must exist and be readable
- Type must match file extension
- Size must be > 0 and < 100MB
- Hash must be valid SHA256

**State Transitions**:
```
NEW → PARSING → PARSED → SUMMARIZING → COMPLETE
     ↓        ↓          ↓
   ERROR    ERROR      ERROR
```

### MeetingNote
Represents meeting notes/transcripts for structured processing.

**Fields**:
- `id`: UUID - Unique identifier
- `title`: string - Meeting title/topic
- `content`: string - Raw meeting notes/transcript
- `participants`: list[string] - Extracted participant names
- `date`: datetime - Meeting date (extracted or provided)
- `overview`: string - Generated overview
- `key_points`: list[string] - Extracted key points
- `action_items`: list[ActionItem] - Extracted action items
- `created_at`: datetime - Processing timestamp

**Relationships**:
- Has many ActionItem entities

### ActionItem
Represents an action item extracted from meeting notes.

**Fields**:
- `id`: UUID - Unique identifier
- `meeting_note_id`: UUID - Foreign key to MeetingNote
- `description`: string - Action item description
- `assignee`: string - Person assigned (if mentioned)
- `due_date`: datetime - Due date (if mentioned)
- `priority`: enum - PRIORITY (HIGH, MEDIUM, LOW)
- `status`: enum - STATUS (OPEN, COMPLETED)

### EmailAccount
Represents configured IMAP email account.

**Fields**:
- `id`: string - User-defined account identifier
- `provider`: enum - PROVIDER (GMAIL, OUTLOOK, CUSTOM)
- `host`: string - IMAP server hostname
- `port`: integer - IMAP server port (default 993)
- `username`: string - Email username
- `credential_key`: string - Keyring reference for password
- `default_mailbox`: string - Default mailbox to process
- `use_tls`: boolean - Enforce TLS connection
- `created_at`: datetime - Account setup timestamp
- `last_sync`: datetime - Last successful sync

**Validation Rules**:
- ID must be unique and alphanumeric
- Host must be valid hostname or IP
- Port must be in range 1-65535
- Username must be valid email format
- Credential must exist in system keyring

### EmailMessage
Represents a processed email with classification and summary.

**Fields**:
- `message_id`: string - Unique email message ID
- `account_id`: string - Foreign key to EmailAccount
- `sender`: string - Sender email address
- `recipients`: list[string] - Recipient email addresses
- `subject`: string - Email subject line
- `date`: datetime - Email date
- `body_text`: string - Plain text email body
- `body_html`: string - HTML email body (optional)
- `classification`: enum - CATEGORY (IMPORTANT, WORK, PERSONAL, PROMOTIONAL, NEWSLETTER, SPAM, ACTION_REQUIRED)
- `priority`: enum - PRIORITY (HIGH, MEDIUM, LOW)
- `summary`: string - Generated summary
- `action_items`: list[string] - Extracted action items
- `processed_at`: datetime - Processing timestamp

**Validation Rules**:
- Message ID must be unique per account
- Sender must be valid email format
- Date must be valid datetime
- Classification must be from predefined categories

### AIProvider
Represents LLM configuration for local or cloud providers.

**Fields**:
- `id`: string - Provider identifier
- `type`: enum - PROVIDER_TYPE (LOCAL, OPENAI, ANTHROPIC)
- `endpoint_url`: string - API endpoint URL
- `model_name`: string - Model identifier
- `api_key_ref`: string - Keyring reference for API key (cloud only)
- `max_tokens`: integer - Maximum context window
- `temperature`: float - Generation temperature (0.0-1.0)
- `timeout_seconds`: integer - Request timeout
- `is_default`: boolean - Default provider flag
- `created_at`: datetime - Setup timestamp

**Validation Rules**:
- ID must be unique
- Type must match endpoint configuration
- Local providers must have accessible endpoint
- Cloud providers must have valid API key
- Only one provider can be default

### ProcessingJob
Represents background processing job status.

**Fields**:
- `id`: UUID - Job identifier
- `type`: enum - JOB_TYPE (DOCUMENT_SUMMARY, EMAIL_PROCESS, MEETING_ANALYSIS)
- `status`: enum - STATUS (QUEUED, RUNNING, COMPLETED, FAILED)
- `input_data`: dict - Job input parameters
- `result_data`: dict - Job output results
- `error_message`: string - Error details (if failed)
- `progress_percent`: integer - Completion percentage
- `created_at`: datetime - Job creation time
- `started_at`: datetime - Job start time
- `completed_at`: datetime - Job completion time

**State Transitions**:
```
QUEUED → RUNNING → COMPLETED
         ↓         ↗
       FAILED ----
```

## Relationships

```
EmailAccount 1:N EmailMessage
MeetingNote 1:N ActionItem
ProcessingJob 1:1 (Document|MeetingNote|EmailMessage)
AIProvider 1:N ProcessingJob
```

## Database Schema Considerations

For this CLI-first application, we'll use:
- **File-based storage** for documents and meeting notes
- **SQLite database** for metadata, email messages, and job tracking
- **System keyring** for sensitive credentials
- **JSON files** for configuration

This approach provides:
- Simple deployment (single binary + config)
- Fast local operations
- Easy backup (copy files)
- No external database dependency
- Secure credential management