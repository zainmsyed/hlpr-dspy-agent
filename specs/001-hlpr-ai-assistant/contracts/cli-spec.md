# CLI Contract Specification

## hlpr summarize

### hlpr summarize document

**Usage**: `hlpr summarize document [OPTIONS] FILE_PATH`

**Description**: Summarize a document (PDF, DOCX, TXT, MD)

**Arguments**:
- `FILE_PATH`: Path to the document file to summarize (required)

**Options**:
- `--provider TEXT`: AI provider to use [local|openai|anthropic] (default: configured default)
- `--save / --no-save`: Save summary to file (default: False)
- `--format [txt|md|json]`: Output format (default: rich terminal output)
- `--output PATH`: Output file path (default: auto-generated)
- `--chunk-size INTEGER`: Chunk size for large documents (default: 8192)
- `--chunk-overlap INTEGER`: Overlap between chunks (default: 256)
- `--help`: Show help message

**Examples**:
```bash
hlpr summarize document report.pdf
hlpr summarize document --provider openai --save --format md notes.docx
hlpr summarize document --output summary.txt document.txt
```

**Output**:
- Rich terminal display with summary and key points
- Optional file output in specified format
- Progress bar for large documents
- Error messages for unsupported files

**Exit Codes**:
- 0: Success
- 1: File not found or unreadable
- 2: Unsupported file format
- 3: LLM provider unavailable
- 4: Processing error

### hlpr summarize meeting

**Usage**: `hlpr summarize meeting [OPTIONS] FILE_PATH`

**Description**: Process meeting notes or transcript into structured summary

**Arguments**:
- `FILE_PATH`: Path to meeting notes file (TXT or MD) (required)

**Options**:
- `--title TEXT`: Meeting title (default: derived from filename)
- `--date TEXT`: Meeting date (ISO format, default: file modification date)
- `--provider TEXT`: AI provider to use (default: configured default)
- `--save / --no-save`: Save structured summary (default: False)
- `--format [txt|md|json]`: Output format (default: rich terminal)
- `--output PATH`: Output file path (default: auto-generated)
- `--help`: Show help message

**Examples**:
```bash
hlpr summarize meeting standup-notes.txt
hlpr summarize meeting --title "Sprint Planning" --date 2025-09-09 meeting.md
hlpr summarize meeting --save --format json transcript.txt
```

**Output**:
- Structured display: Overview, Key Points, Action Items, Participants
- Rich terminal formatting with sections and bullet points
- Optional file output with structured data

## hlpr email

### hlpr email process

**Usage**: `hlpr email process [OPTIONS] ACCOUNT_ID`

**Description**: Process emails from configured IMAP account

**Arguments**:
- `ACCOUNT_ID`: Email account identifier (required)

**Options**:
- `--mailbox TEXT`: Mailbox/folder name (default: INBOX)
- `--unread-only / --all`: Process only unread emails (default: unread-only)
- `--since DATE`: Process emails since date (YYYY-MM-DD format)
- `--from TEXT`: Filter by sender email address
- `--limit INTEGER`: Maximum emails to process (default: 50, max: 1000)
- `--provider TEXT`: AI provider for classification (default: configured default)
- `--save / --no-save`: Save results to file (default: False)
- `--format [table|json|csv]`: Output format (default: table)
- `--output PATH`: Output file path (default: auto-generated)
- `--help`: Show help message

**Examples**:
```bash
hlpr email process personal
hlpr email process work --mailbox "Important" --since 2025-09-01
hlpr email process gmail --unread-only --limit 20 --save --format csv
```

**Output**:
- Rich table with: Sender, Subject, Date, Classification, Priority
- Progress bar during processing
- Summary statistics (total processed, by category)
- Optional file export

### hlpr email accounts

**Usage**: `hlpr email accounts [COMMAND] [OPTIONS]`

**Description**: Manage email account configurations

**Commands**:

#### hlpr email accounts list

**Usage**: `hlpr email accounts list`

**Description**: List configured email accounts

**Output**:
- Table with: ID, Provider, Username, Host, Last Sync
- Status indicators for each account

#### hlpr email accounts add

**Usage**: `hlpr email accounts add [OPTIONS] ACCOUNT_ID`

**Arguments**:
- `ACCOUNT_ID`: Unique identifier for the account (required)

**Options**:
- `--provider [gmail|outlook|custom]`: Email provider (required)
- `--username TEXT`: Email username (required)
- `--password TEXT`: Password or app password (prompted if not provided)
- `--host TEXT`: IMAP server hostname (auto-detected for gmail/outlook)
- `--port INTEGER`: IMAP server port (default: 993)
- `--mailbox TEXT`: Default mailbox (default: INBOX)
- `--no-tls`: Disable TLS (not recommended)
- `--test / --no-test`: Test connection after adding (default: True)
- `--help`: Show help message

**Examples**:
```bash
hlpr email accounts add personal --provider gmail --username user@gmail.com
hlpr email accounts add work --provider outlook --username user@company.com
hlpr email accounts add custom --provider custom --host mail.example.com --username user@example.com
```

#### hlpr email accounts remove

**Usage**: `hlpr email accounts remove ACCOUNT_ID`

**Arguments**:
- `ACCOUNT_ID`: Account identifier to remove (required)

**Options**:
- `--confirm / --no-confirm`: Skip confirmation prompt (default: False)
- `--help`: Show help message

#### hlpr email accounts test

**Usage**: `hlpr email accounts test ACCOUNT_ID`

**Arguments**:
- `ACCOUNT_ID`: Account identifier to test (required)

**Description**: Test IMAP connection for configured account

**Output**:
- Connection status and basic mailbox information

## hlpr config

### hlpr config show

**Usage**: `hlpr config show [OPTIONS]`

**Description**: Display current configuration

**Options**:
- `--format [yaml|json]`: Output format (default: yaml)
- `--hide-sensitive`: Hide sensitive values (default: True)
- `--help`: Show help message

### hlpr config set

**Usage**: `hlpr config set KEY VALUE`

**Arguments**:
- `KEY`: Configuration key (required)
- `VALUE`: Configuration value (required)

**Description**: Set configuration value

**Examples**:
```bash
hlpr config set default_llm openai
hlpr config set local_llm_endpoint http://localhost:11434
hlpr config set openai.model gpt-4
```

### hlpr config get

**Usage**: `hlpr config get KEY`

**Arguments**:
- `KEY`: Configuration key (required)

**Description**: Get configuration value

## hlpr providers

### hlpr providers list

**Usage**: `hlpr providers list`

**Description**: List configured AI providers and their status

**Output**:
- Table with: ID, Type, Model, Status, Default
- Status indicators (available/unavailable/error)

### hlpr providers add

**Usage**: `hlpr providers add [OPTIONS] PROVIDER_ID`

**Arguments**:
- `PROVIDER_ID`: Unique identifier for the provider (required)

**Options**:
- `--type [local|openai|anthropic]`: Provider type (required)
- `--model TEXT`: Model name (required)
- `--endpoint TEXT`: API endpoint URL (for local providers)
- `--api-key TEXT`: API key (for cloud providers, prompted if not provided)
- `--max-tokens INTEGER`: Maximum context window (default: auto-detect)
- `--temperature FLOAT`: Generation temperature 0.0-1.0 (default: 0.7)
- `--timeout INTEGER`: Request timeout in seconds (default: 30)
- `--default / --no-default`: Set as default provider (default: False)
- `--test / --no-test`: Test provider after adding (default: True)
- `--help`: Show help message

### hlpr providers test

**Usage**: `hlpr providers test PROVIDER_ID`

**Arguments**:
- `PROVIDER_ID`: Provider identifier to test (required)

**Description**: Test AI provider connection and response

## Global Options

Available for all commands:

- `--verbose / --no-verbose`: Enable verbose output (default: False)
- `--quiet / --no-quiet`: Suppress non-essential output (default: False)
- `--config PATH`: Custom configuration file path
- `--help`: Show help message
- `--version`: Show version information

## Exit Codes

Standard exit codes used across all commands:

- `0`: Success
- `1`: General error (file not found, invalid input, etc.)
- `2`: Configuration error (missing config, invalid settings)
- `3`: Authentication error (invalid credentials, API key)
- `4`: Network error (connection failed, timeout)
- `5`: Provider error (LLM unavailable, quota exceeded)
- `6`: Processing error (parsing failed, unsupported format)

## Environment Variables

- `HLPR_CONFIG_PATH`: Override default config file location
- `HLPR_LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `HLPR_NO_COLOR`: Disable colored output
- `HLPR_API_KEY_*`: API keys for cloud providers (e.g., HLPR_API_KEY_OPENAI)