# Data Model: Enhanced CLI/TUI for Document Summarization

## Core Entities

### InteractiveSession
**Purpose**: Manages the guided mode user workflow state  
**Fields**:
- `session_id`: str - Unique identifier for the session
- `current_step`: str - Current workflow step (file_selection, provider_choice, options, processing, results)
- `selected_files`: List[Path] - Files selected for processing
- `provider_config`: Dict[str, Any] - Selected provider and model settings
- `output_preferences`: OutputPreferences - User's output format and save preferences
- `processing_state`: ProcessingState - Current processing status and results

**State Transitions**:
```
start → file_selection → provider_choice → options → processing → results → end
```

**Validation Rules**:
- At least one file must be selected before proceeding to provider_choice
- Provider must be valid and available
- File paths must exist and be readable
- Output path must be writable if specified

### OutputPreferences
**Purpose**: Encapsulates user preferences for output formatting and saving  
**Fields**:
- `format`: str - Output format (rich, txt, md, json)
- `save_to_file`: bool - Whether to save output to file
- `output_path`: Optional[Path] - Custom output file path
- `show_metadata`: bool - Whether to display processing metadata
- `verbose_mode`: bool - Whether to show detailed processing information

**Validation Rules**:
- format must be one of: rich, txt, md, json
- output_path must be valid file path if specified
- output_path directory must exist and be writable

### ProcessingState
**Purpose**: Tracks the current state of document processing  
**Fields**:
- `status`: str - Current status (idle, parsing, chunking, summarizing, complete, error)
- `current_file`: Optional[Path] - File currently being processed
- `progress`: float - Overall progress percentage (0.0 to 1.0)
- `phase`: str - Current processing phase description
- `start_time`: datetime - Processing start timestamp
- `results`: List[ProcessingResult] - Completed processing results
- `errors`: List[ProcessingError] - Any errors encountered

**State Transitions**:
```
idle → parsing → chunking → summarizing → complete
idle → parsing → error
chunking → error (with partial results)
summarizing → error (with partial results)
```

### ProcessingResult
**Purpose**: Contains the results of processing a single document  
**Fields**:
- `file_path`: Path - Path to the processed file
- `summary`: str - Generated summary text
- `key_points`: List[str] - Extracted key points
- `metadata`: ProcessingMetadata - Processing details and statistics
- `processing_time_ms`: int - Time taken to process this file

### ProcessingMetadata
**Purpose**: Detailed information about how processing was performed  
**Fields**:
- `file_size_bytes`: int - Original file size
- `document_format`: str - File format (PDF, DOCX, TXT, MD)
- `provider_used`: str - AI provider that processed the document
- `model_used`: str - Specific model name
- `temperature`: float - Temperature setting used
- `chunk_count`: int - Number of chunks if chunking was used
- `chunk_strategy`: str - Chunking strategy applied

### ProcessingError
**Purpose**: Structured error information with user guidance  
**Fields**:
- `file_path`: Optional[Path] - File that caused the error (if applicable)
- `error_type`: str - Category of error (file_not_found, unsupported_format, processing_failed, etc.)
- `message`: str - Human-readable error message
- `suggestion`: str - Actionable suggestion for the user
- `technical_details`: Optional[str] - Technical error details (for verbose mode)

### FileSelection
**Purpose**: Represents a file selection in the guided mode  
**Fields**:
- `path`: Path - File path
- `display_name`: str - Friendly name for display
- `size_bytes`: int - File size for display
- `format`: str - Detected file format
- `is_valid`: bool - Whether file can be processed
- `validation_message`: Optional[str] - Reason if file is not valid

### ProviderOption
**Purpose**: Represents an available AI provider option  
**Fields**:
- `provider_id`: str - Unique identifier (local, openai, anthropic, etc.)
- `display_name`: str - User-friendly name
- `description`: str - Brief description of the provider
- `is_available`: bool - Whether provider is currently available
- `models`: List[str] - Available models for this provider
- `default_model`: str - Default model for this provider

## Relationships

### InteractiveSession → OutputPreferences (1:1)
Each interactive session has one set of output preferences that persist through the session.

### InteractiveSession → ProcessingState (1:1)
Each interactive session maintains one processing state that tracks all files being processed.

### ProcessingState → ProcessingResult (1:many)
A processing state contains multiple results, one for each file processed.

### ProcessingState → ProcessingError (1:many)  
A processing state may contain multiple errors encountered during processing.

### ProcessingResult → ProcessingMetadata (1:1)
Each processing result has associated metadata about how it was generated.

## Data Flow

### Guided Mode Flow
```
1. User starts `hlpr summarize`
2. InteractiveSession created with empty state
3. File selection populates InteractiveSession.selected_files
4. Provider selection populates InteractiveSession.provider_config
5. Options selection populates InteractiveSession.output_preferences
6. Processing begins, updating ProcessingState in real-time
7. Results accumulated in ProcessingState.results
8. Final output rendered using OutputPreferences
```

### Direct Command Flow
```
1. User runs `hlpr summarize document file.pdf --provider local --format json`
2. OutputPreferences created from CLI arguments
3. ProcessingState created for single file
4. Processing begins immediately
5. Result rendered in specified format
```

## Validation and Error Handling

### File Validation
- File existence and readability
- Supported format detection
- File size limits (configured in settings)
- Permission checks for output paths

### Provider Validation
- Provider availability (network/local service)
- Model availability for selected provider
- Configuration validation (API keys, endpoints)
- Parameter validation (temperature range, etc.)

### Processing Validation
- Document parsing success
- Chunking strategy compatibility
- Output format compatibility
- Disk space for output files

## Storage Requirements

### In-Memory Only
All entities are transient and exist only during command execution. No persistent storage required.

### Temporary Files
- Partial results may be cached during processing of very large files
- Temporary files cleaned up on process completion or interruption

### Configuration Persistence
Output preferences and provider settings may be saved to user config for future sessions (handled by existing config system).

## Performance Considerations

### Memory Usage
- ProcessingState maintains minimal state during processing
- Results are streamed to output rather than accumulated when possible
- Large file processing uses chunked approach with bounded memory

### Concurrent Processing
- Multiple files can be processed in parallel
- ProcessingState tracks per-file progress
- Errors in one file don't stop processing of others

### Progress Tracking
- Progress calculation based on processing phases
- Real-time updates to ProcessingState.progress
- Efficient progress reporting without impacting processing performance