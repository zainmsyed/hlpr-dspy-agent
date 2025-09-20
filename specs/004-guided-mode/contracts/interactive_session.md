# Interactive Session Contracts

**Module**: `src/hlpr/cli/interactive.py`  
**Purpose**: Define method signatures for enhanced guided workflow functionality

## Core Interface Contracts

### 1. Enhanced InteractiveSession Methods

```python
class InteractiveSession:
    """Enhanced interactive session for guided document processing."""
    
    def collect_basic_options(self) -> ProcessingOptions:
        """
        Collect Tier 1 (basic) user options through Rich prompts.
        
        Returns:
            ProcessingOptions: Validated basic configuration
            
        Prompts for:
        - AI Provider (default: local)
        - Output Format (default: rich) 
        - Save to File (default: no)
        - Output Path (if saving)
        
        Validation:
        - Provider must be in supported list
        - Format must be supported output type
        - Path must be valid if saving enabled
        
        Error Handling:
        - Invalid input re-prompts with error message
        - Shows available choices on validation failure
        - Allows default selection via Enter key
        """
        
    def collect_advanced_options(self, base_options: ProcessingOptions) -> ProcessingOptions:
        """
        Collect Tier 2 (advanced) options if user requests them.
        
        Args:
            base_options: Basic options to enhance
            
        Returns:
            ProcessingOptions: Enhanced with advanced settings
            
        Prompts for:
        - Model name (default: gemma3:latest)
        - Temperature (default: 0.3, range: 0.0-1.0)
        - Chunk Size (default: 8192, range: 1-32768)
        - Chunk Overlap (default: 256, range: 0+)
        - Chunking Strategy (default: sentence)
        - Verify Hallucinations (default: no)
        
        Validation:
        - Temperature within 0.0-1.0 range
        - Chunk size positive integer
        - Overlap non-negative, typically < chunk_size
        
        Error Handling:
        - Numeric validation with range checking
        - Re-prompt on invalid values with constraints shown
        - Type conversion errors show helpful messages
        """
        
    def process_document_with_options(self, file_path: str, options: ProcessingOptions) -> SummarizationResult:
        """
        Process document using collected options and existing CLI pipeline.
        
        Args:
            file_path: Path to document file
            options: User-selected processing configuration
            
        Returns:
            SummarizationResult: Processing results with summary and metadata
            
        Processing Flow:
        1. Convert options to CLI arguments
        2. Call _parse_with_progress(file_path, verbose=True)
        3. Call _summarize_with_progress(...) with options
        4. Handle progress display through existing Rich infrastructure
        
        Progress Display:
        - Phase 1: Parsing document (existing progress bar)
        - Phase 2: Chunking (if needed, show strategy)  
        - Phase 3: Summarization (show model/provider)
        
        Error Handling:
        - File not found or unreadable
        - Parsing errors (unsupported format, corrupted)
        - Summarization errors (model unavailable, timeout)
        - Uses existing CLI error panels and recovery
        """
        
    def generate_command_template(self, options: ProcessingOptions) -> CommandTemplate:
        """
        Generate reusable CLI command template from options.
        
        Args:
            options: Processing configuration to convert
            
        Returns:
            CommandTemplate: Template with placeholder and metadata
            
        Template Format:
        - Base command: "hlpr summarize document [PASTE FILE PATH HERE]"
        - Options as CLI flags: "--provider local --format rich"
        - Multi-line formatting for readability
        - Includes all non-default option values
        
        Metadata:
        - Unique timestamp-based ID
        - Creation timestamp
        - Usage count (initially 0)
        - Option values for future reference
        """
        
    def display_command_template(self, template: CommandTemplate) -> None:
        """
        Display generated command template with Rich formatting.
        
        Args:
            template: Command template to display
            
        Display Format:
        - Rich panel with command template
        - Syntax highlighting for CLI command
        - Copy/paste instructions
        - Save template prompt
        
        User Interaction:
        - Ask to save template to history (y/N)
        - Show successful save confirmation
        - Handle save errors gracefully
        """
        
    def handle_keyboard_interrupt(self) -> bool:
        """
        Handle Ctrl+C gracefully with confirmation.
        
        Returns:
            bool: True if user confirmed exit, False to continue
            
        Behavior:
        - First Ctrl+C: Show exit confirmation
        - Second Ctrl+C or 'q': Return True (exit)
        - Any other key: Return False (continue)
        
        Display:
        - Clear exit message
        - Instructions for confirming or continuing
        - No data corruption on exit
        """
```

### 2. Option Collection Interface

```python
class OptionPrompts:
    """Rich-formatted prompts for interactive option collection."""
    
    def provider_prompt(self) -> str:
        """
        Prompt for AI provider selection.
        
        Returns:
            str: Selected provider name
            
        Contract:
        - Shows available providers as choices
        - Default: "local"
        - Validates against supported list
        - Re-prompts on invalid selection
        """
        
    def format_prompt(self) -> str:
        """Prompt for output format selection."""
        
    def save_file_prompt(self) -> bool:
        """Prompt whether to save output to file."""
        
    def output_path_prompt(self, default_name: Optional[str] = None) -> str:
        """Prompt for output file path with suggested default."""
        
    def temperature_prompt(self) -> float:
        """Prompt for model temperature (advanced option)."""
        
    def chunk_size_prompt(self) -> int:
        """Prompt for chunk size (advanced option)."""
        
    def advanced_options_prompt(self) -> bool:
        """Ask if user wants advanced options."""
```

### 3. Command Template Management

```python
class SavedCommands:
    """Persistent storage manager for command templates."""
    
    def save_command(self, template: CommandTemplate) -> bool:
        """
        Save command template to persistent storage.
        
        Args:
            template: Template to save
            
        Returns:
            bool: True if saved successfully, False on error
            
        Storage:
        - Location: ~/.hlpr/saved_commands.json
        - Format: JSON with template list
        - Atomic writes to prevent corruption
        
        Error Handling:
        - Directory creation if needed
        - File permission errors
        - Disk space issues
        - Malformed existing data recovery
        """
        
    def load_commands(self) -> List[CommandTemplate]:
        """Load all saved templates from storage."""
        
    def delete_command(self, command_id: str) -> bool:
        """Delete template by ID."""
```

## Data Validation Contracts

### ProcessingOptions Validation

```python
# Input validation rules enforced by Pydantic
class ProcessingOptions(BaseModel):
    provider: Literal["local", "openai", "anthropic", "groq", "together"] = "local"
    format: Literal["rich", "txt", "md", "json"] = "rich"
    temperature: float = Field(0.3, ge=0.0, le=1.0)  # Range: 0.0-1.0
    chunk_size: int = Field(8192, gt=0, le=32768)     # Range: 1-32768
    chunk_overlap: int = Field(256, ge=0)             # Range: 0+
    
    @field_validator('output_path')
    def validate_output_path(cls, v, info):
        """Validate output path when save_to_file is True."""
        if info.data.get('save_to_file') and not v:
            raise ValueError('output_path required when save_to_file is True')
        return v
```

## CLI Integration Contracts

### Argument Conversion

```python
ProcessingOptions.to_cli_args() -> List[str]
"""
Convert interactive options to CLI argument format.

Input: ProcessingOptions instance
Output: List of CLI arguments ready for subprocess call

Example:
options = ProcessingOptions(provider="local", format="rich", temperature=0.5)
args = options.to_cli_args()
# Returns: ["--provider", "local", "--format", "rich", "--temperature", "0.5"]
"""
```

### Progress Integration

```python
# Reuse existing progress functions with options
_parse_with_progress(file_path: str, verbose: bool = True) -> str
_summarize_with_progress(document: Document, options: Dict[str, Any]) -> SummarizationResult  
_display_summary(document: Document, result: SummarizationResult, format: str) -> None
```

---

**Contract Status**: ✅ Complete  
**Test Coverage**: Each contract requires corresponding test methods  
**Integration**: All contracts use existing CLI infrastructure and error handling