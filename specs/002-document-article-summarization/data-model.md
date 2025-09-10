# Data Model: Document & Article Summarization

## Core Entities

### Document
Represents a file for processing and summarization.

**Fields**:
- `id`: UUID - Unique identifier
- `path`: string - Absolute file path
- `format`: enum - FILE_FORMAT (PDF, DOCX, TXT, MD)
- `size_bytes`: integer - File size for chunking decisions
- `content_hash`: string - SHA256 hash for caching
- `extracted_text`: string - Raw extracted text content
- `summary`: string - Generated summary
- `key_points`: list[string] - Extracted key points
- `processing_time_ms`: integer - Time taken to process
- `created_at`: datetime - Processing timestamp
- `updated_at`: datetime - Last modification

**Validation Rules**:
- Path must exist and be readable
- Format must match file extension
- Size must be > 0 and < 100MB
- Hash must be valid SHA256

**State Transitions**:
```
NEW → PARSING → PARSED → SUMMARIZING → COMPLETE
     ↓        ↓          ↓
   ERROR    ERROR      ERROR
```

## Relationships

This feature focuses on the Document entity with processing metadata. The entity integrates with the broader hlpr system for LLM provider management and configuration.