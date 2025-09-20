# Data Model: Guided Workflow Data Structures

**Feature**: Robust Guided Workflow for Document Summarization  
**Phase**: 1 - Design & Contracts  
**Date**: September 20, 2025

## Core Entities

### 1. ProcessingOptions
**Purpose**: Type-safe container for user-selected processing configuration  
**Location**: `src/hlpr/models/interactive.py`

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal

class ProcessingOptions(BaseModel):
    """User-selected options for document processing."""
    
    # Basic Options (Tier 1)
    provider: Literal["local", "openai", "anthropic", "groq", "together"] = "local"
    format: Literal["rich", "txt", "md", "json"] = "rich"
    save_to_file: bool = False
    output_path: Optional[str] = None
    
    # Advanced Options (Tier 2) 
    model: str = "gemma3:latest"
    temperature: float = Field(0.3, ge=0.0, le=1.0)
    chunk_size: int = Field(8192, gt=0, le=32768)
    chunk_overlap: int = Field(256, ge=0)
    chunking_strategy: Literal["sentence", "paragraph", "fixed", "token"] = "sentence"
    verify_hallucinations: bool = False
    
    class Config:
        validate_assignment = True
        
    def to_cli_args(self) -> list[str]:
        """Convert options to CLI argument list."""
        args = [
            "--provider", self.provider,
            "--format", self.format,
            "--temperature", str(self.temperature),
            "--chunk-size", str(self.chunk_size)
        ]
        
        if self.save_to_file and self.output_path:
            args.extend(["--save", "--output", self.output_path])
            
        if self.verify_hallucinations:
            args.append("--verify")
            
        return args
```

**Validation Rules**:
- `temperature`: Must be between 0.0 and 1.0
- `chunk_size`: Must be positive, max 32768 for performance
- `chunk_overlap`: Must be non-negative, typically less than chunk_size
- `output_path`: Required when `save_to_file` is True

**State Transitions**:
- Default → User Modified → Validated → CLI Args

### 2. CommandTemplate
**Purpose**: Reusable CLI command with metadata for future execution  
**Location**: `src/hlpr/models/templates.py`

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any

class CommandTemplate(BaseModel):
    """Template for reusable CLI commands."""
    
    id: str
    name: Optional[str] = None
    command_template: str  # e.g., "hlpr summarize document {file} --provider {provider}"
    options: Dict[str, Any]
    description: Optional[str] = None
    created: datetime
    usage_count: int = 0
    last_used: Optional[datetime] = None
    
    @classmethod
    def from_options(cls, options: ProcessingOptions) -> "CommandTemplate":
        """Generate template from processing options."""
        template_str = "hlpr summarize document [PASTE FILE PATH HERE]"
        
        for arg in options.to_cli_args():
            if not arg.startswith("--"):
                template_str += f" {arg}"
            else:
                template_str += f" \\\n  {arg}"
                
        return cls(
            id=f"cmd_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            command_template=template_str,
            options=options.model_dump(),
            created=datetime.now()
        )
        
    def to_executable_command(self, file_path: str) -> str:
        """Generate executable command with file path."""
        return self.command_template.replace("[PASTE FILE PATH HERE]", file_path)
```

**Relationships**:
- Generated from `ProcessingOptions`
- Stored in `SavedCommands` collection
- Used by command template display system

### 3. InteractiveSession (Enhanced)
**Purpose**: Manages guided workflow state and user interactions  
**Location**: `src/hlpr/cli/interactive.py` (enhanced existing class)

```python
from dataclasses import dataclass
from typing import Optional
from .models.interactive import ProcessingOptions
from .models.templates import CommandTemplate

@dataclass
class InteractiveSession:
    """Enhanced interactive session for guided workflow."""
    
    # Existing fields
    console: Console
    progress_tracker: ProgressTracker
    
    # New fields for enhanced functionality
    options: Optional[ProcessingOptions] = None
    template: Optional[CommandTemplate] = None
    file_path: Optional[str] = None
    
    def collect_basic_options(self) -> ProcessingOptions:
        """Collect Tier 1 (basic) options from user."""
        
    def collect_advanced_options(self, options: ProcessingOptions) -> ProcessingOptions:
        """Collect Tier 2 (advanced) options if requested."""
        
    def generate_template(self) -> CommandTemplate:
        """Generate command template from collected options."""
        
    def save_template(self, template: CommandTemplate) -> bool:
        """Save template to user's command history."""
```

**State Flow**:
1. Initial → Options Collection
2. Options Collection → Processing
3. Processing → Results Display  
4. Results Display → Template Generation
5. Template Generation → Complete

### 4. OptionPrompts
**Purpose**: Rich-formatted prompts for option collection  
**Location**: `src/hlpr/cli/prompts.py` (new module)

```python
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from rich.console import Console
from typing import Literal, Optional

class OptionPrompts:
    """Rich-formatted prompts for guided option collection."""
    
    def __init__(self, console: Console):
        self.console = console
        
    def provider_prompt(self) -> str:
        """Prompt for AI provider selection."""
        return Prompt.ask(
            "[bold blue]AI Provider[/bold blue]",
            choices=["local", "openai", "anthropic", "groq", "together"],
            default="local",
            show_choices=True,
            show_default=True
        )
        
    def format_prompt(self) -> str:
        """Prompt for output format selection."""
        
    def temperature_prompt(self) -> float:
        """Prompt for model temperature setting."""
        
    def advanced_options_prompt(self) -> bool:
        """Ask if user wants to configure advanced options."""
        return Confirm.ask(
            "[bold yellow]Configure advanced options?[/bold yellow]",
            default=False
        )
```

### 5. SavedCommands
**Purpose**: Persistent storage and management of command templates  
**Location**: `src/hlpr/models/saved_commands.py` (new module)

```python
from pathlib import Path
from typing import List, Optional
import json
from .templates import CommandTemplate

class SavedCommands:
    """Manager for persistent command template storage."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / ".hlpr" / "saved_commands.json"
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
    def load_commands(self) -> List[CommandTemplate]:
        """Load all saved command templates."""
        
    def save_command(self, template: CommandTemplate) -> bool:
        """Save a new command template."""
        
    def delete_command(self, command_id: str) -> bool:
        """Delete a command template by ID."""
        
    def increment_usage(self, command_id: str) -> bool:
        """Increment usage count for a template."""
```

**Storage Schema**:
```json
{
  "version": "1.0",
  "commands": [
    {
      "id": "cmd_20250920_103000",
      "name": "Local Rich Processing",
      "command_template": "hlpr summarize document [PASTE FILE PATH HERE] --provider local --format rich",
      "options": {"provider": "local", "format": "rich"},
      "description": "Fast local processing with rich terminal output",
      "created": "2025-09-20T10:30:00Z",
      "usage_count": 3,
      "last_used": "2025-09-20T14:15:00Z"
    }
  ]
}
```

## Entity Relationships

```
ProcessingOptions 
    ↓ (generates)
CommandTemplate 
    ↓ (stored by)
SavedCommands
    ↑ (managed by)
InteractiveSession
    ↓ (uses)
OptionPrompts
```

## Validation & Constraints

### Input Validation
- **Provider**: Must be one of supported providers
- **Format**: Must be one of supported output formats  
- **Temperature**: Numeric range validation (0.0-1.0)
- **Chunk Size**: Positive integer, reasonable upper bound
- **File Paths**: Existence and readability checks

### Business Rules
- Advanced options only collected if user requests them
- Output path required when save_to_file is True
- Command templates always include file path placeholder
- Saved commands have unique IDs and timestamps

### Error Handling
- Invalid option values trigger re-prompt with error message
- File system errors during save show warning but don't block workflow
- Malformed saved command data falls back to empty collection

---

**Data Model Status**: ✅ Complete  
**Next**: Contracts generation and test creation  
**Dependencies**: Pydantic models, Rich prompt library, existing CLI infrastructure