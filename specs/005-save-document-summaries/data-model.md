# Data Model: Save Document Summaries in Organized Folder Structure

## Core Entities

### OutputPath
Represents the resolved file path for saving summaries.

**Fields**:
- `original_document_path`: str - Source document file path
- `custom_output_path`: Optional[str] - User-specified output path via `--output`
- `resolved_path`: Path - Final computed file path for saving
- `is_organized`: bool - Whether using organized folder structure
- `created_directories`: List[Path] - Directories created during resolution

**Validation Rules**:
- `resolved_path` must be writable location
- `custom_output_path` when provided must be valid file path
- `created_directories` must have appropriate permissions

**State Transitions**:
```
New → Path Resolution → Directory Creation → Ready for Write
  ↓         ↓              ↓                   ↓
custom?   resolve()    ensure_dirs()      write_summary()
```

### OrganizedStorage
Configuration and utilities for organized folder structure.

**Fields**:
- `base_directory`: Path - Base location for organized storage (default: current working directory)
- `summaries_folder`: str - Folder name for summaries (default: "hlpr/summaries/documents")
- `default_format`: str - Default file format (default: "md")
- `create_missing_dirs`: bool - Whether to create directories automatically (default: True)

**Methods**:
- `get_organized_path(document_path: str, format: str) -> Path` - Generate organized file path
- `ensure_directory_exists() -> bool` - Create directory structure if needed
- `is_path_in_organized_structure(path: Path) -> bool` - Check if path uses organized structure

**Validation Rules**:
- `base_directory` must be readable and writable
- `summaries_folder` must be valid directory name
- `default_format` must be supported format (txt, md, json)

### SummaryFileInfo
Metadata about a saved summary file.

**Fields**:
- `summary_path`: Path - Where the summary was saved
- `original_document`: str - Source document filename
- `format`: str - File format used (txt, md, json)
- `created_at`: datetime - When file was created
- `file_size_bytes`: int - Size of generated summary file
- `used_organized_structure`: bool - Whether organized folder structure was used

**Validation Rules**:
- `summary_path` must exist after creation
- `format` must match file extension
- `file_size_bytes` must be > 0

## Enhanced Entities (Existing)

### Document (Extended)
Existing document model with enhanced save capabilities.

**New Fields**:
- `preferred_output_format`: Optional[str] - User's preferred format for this document
- `save_location`: Optional[Path] - Where summary was saved (if applicable)
- `uses_organized_storage`: Optional[bool] - Whether saved using organized structure

### OutputPreferences (Enhanced)
Extended version of existing output preferences.

**Enhanced Fields**:
- `use_organized_storage`: bool = True - Whether to use organized folder structure by default
- `organized_base_path`: Optional[Path] = None - Custom base path for organized storage
- `default_summary_format`: str = "md" - Default format for summaries (changed from txt)
- `create_directories_automatically`: bool = True - Auto-create missing directories

## Data Flow

### Path Resolution Flow
```python
def determine_output_path(document: Document, custom_output: Optional[str], format: str) -> OutputPath:
    if custom_output:
        # Use exact custom path - bypass organized structure
        return OutputPath(
            original_document_path=document.path,
            custom_output_path=custom_output,
            resolved_path=Path(custom_output),
            is_organized=False
        )
    else:
        # Use organized structure
        storage = OrganizedStorage()
        organized_path = storage.get_organized_path(document.path, format)
        storage.ensure_directory_exists()
        
        return OutputPath(
            original_document_path=document.path,
            custom_output_path=None,
            resolved_path=organized_path,
            is_organized=True,
            created_directories=[organized_path.parent]
        )
```

### Directory Creation Flow
```python
def ensure_summary_directory(base_path: Path = Path.cwd()) -> Path:
    summary_dir = base_path / "hlpr" / "summaries" / "documents"
    summary_dir.mkdir(parents=True, exist_ok=True)
    return summary_dir
```

### File Naming Convention
```python
def generate_summary_filename(document_path: str, format: str) -> str:
    document_stem = Path(document_path).stem
    return f"{document_stem}_summary.{format}"
```

## Relationships

```
Document 1---1 OutputPath: "has output path"
OutputPath *---1 OrganizedStorage: "uses storage config"
OutputPath 1---1 SummaryFileInfo: "creates file info"
OrganizedStorage 1---* SummaryFileInfo: "manages multiple files"
```

## Storage Schema

### File System Structure
```
{base_directory}/
└── hlpr/
    └── summaries/
        └── documents/
            ├── document1_summary.md
            ├── document2_summary.json
            └── document3_summary.txt
```

### Metadata (Future Extension)
```json
// hlpr/summaries/documents/.metadata.json
{
  "created_at": "2025-09-28T10:30:00Z",
  "total_summaries": 3,
  "formats": ["md", "json", "txt"],
  "last_updated": "2025-09-28T14:45:00Z"
}
```

## Error Handling

### Error Scenarios
1. **Permission Denied**: Cannot create directories or write files
2. **Disk Full**: Insufficient space for directory/file creation
3. **Invalid Path**: Custom output path contains invalid characters
4. **Path Too Long**: Generated path exceeds system limits

### Error Recovery
- Fall back to current directory if organized structure creation fails
- Provide specific error messages with troubleshooting guidance
- Log errors for debugging while maintaining user experience

## Validation Rules

### Path Validation
- All paths must be within accessible file system boundaries
- Custom paths must not overwrite system files
- Directory names must not contain invalid characters

### Format Validation
- Supported formats: txt, md, json
- Format must match file extension in resolved path
- Default format validation ensures known format

### Permission Validation
- Base directory must be writable
- Created directories must inherit appropriate permissions
- Files must be writable after creation

## Future Extensions

### Enhanced Metadata
- Track summary generation statistics
- Support for tagging and categorization
- Search index for summary discovery

### Configuration Persistence
- Save user preferences for organized storage
- Per-project storage configuration
- Custom naming templates

### Batch Operations
- Metadata for batch processing sessions
- Progress tracking for multiple documents
- Atomic operations for batch saves

*Data model complete: All entities defined with clear relationships and validation rules*