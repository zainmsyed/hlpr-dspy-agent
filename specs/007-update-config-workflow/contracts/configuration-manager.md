# Configuration Manager API Contract

**Date**: September 30, 2025  
**Status**: Complete  

## Interface Definition

```python
from abc import ABC, abstractmethod
from typing import Optional
from pathlib import Path

class ConfigurationManagerInterface(ABC):
    """Abstract interface for configuration management"""
    
    @abstractmethod
    def load_configuration(self) -> ConfigurationState:
        """Load configuration from files, with graceful fallback to defaults"""
        pass
    
    @abstractmethod
    def save_configuration(self, config: ConfigurationState) -> None:
        """Save configuration to files atomically"""
        pass
    
    @abstractmethod
    def validate_configuration(self, config: ConfigurationState) -> ValidationResult:
        """Validate configuration and return result with errors/warnings"""
        pass
    
    @abstractmethod
    def reset_to_defaults(self) -> ConfigurationState:
        """Reset configuration to defaults and remove custom files"""
        pass
    
    @abstractmethod
    def get_api_key(self, provider: ProviderType) -> Optional[str]:
        """Get API key for specific provider"""
        pass
    
    @abstractmethod
    def set_api_key(self, provider: ProviderType, api_key: str) -> None:
        """Set API key for specific provider"""
        pass
    
    @abstractmethod
    def is_first_run(self) -> bool:
        """Check if this is first run (no config files exist)"""
        pass
    
    @abstractmethod
    def create_backup(self) -> Path:
        """Create backup of current configuration"""
        pass
```

## Method Contracts

### load_configuration()
**Purpose**: Load complete configuration state from files  
**Returns**: `ConfigurationState` - always valid, with defaults for missing/invalid values  
**Side Effects**: 
- Creates default config directory if missing
- Migrates old configuration formats if detected
- Logs warnings for invalid values found

**Error Handling**:
- File not found → Use defaults
- Corrupted YAML → Use defaults, warn user
- Invalid permissions → Use defaults, warn about security
- Disk I/O errors → Use defaults, report error

### save_configuration(config)
**Purpose**: Save configuration state to files atomically  
**Parameters**: `config: ConfigurationState` - validated configuration  
**Side Effects**:
- Creates backup before overwrite
- Sets file permissions (config.yaml: 644, .env: 600)
- Atomic write (temp file + rename)

**Error Handling**:
- Permission denied → Raise ConfigurationError with fix suggestions
- Disk full → Raise ConfigurationError, preserve original files
- Invalid config → Validate first, raise ValidationError

### validate_configuration(config)
**Purpose**: Validate configuration object completely  
**Returns**: `ValidationResult` with detailed errors/warnings  
**Validation Rules**:
- All enum values within allowed ranges
- Numeric values within constraints
- Paths exist and are accessible
- API keys format valid (if provided)

### reset_to_defaults()
**Purpose**: Reset to factory defaults  
**Returns**: `ConfigurationState` with default values  
**Side Effects**:
- Creates backup of existing configuration
- Removes custom config files
- Preserves API keys unless explicitly requested

### get_api_key(provider) / set_api_key(provider, key)
**Purpose**: Secure API key management  
**Security**: 
- Never logs or prints API keys
- Validates provider enum value
- Ensures .env file has 600 permissions

## CLI Command Contracts

### hlpr config setup
**Purpose**: Interactive configuration setup  
**Flow**:
1. Detect if first run or modification
2. Present current values as defaults
3. Collect user preferences via Rich prompts
4. Validate input incrementally
5. Save configuration and report success

**Exit Codes**:
- 0: Success
- 1: User cancelled
- 2: Validation error
- 3: File system error

### hlpr config show
**Purpose**: Display current configuration  
**Options**:
- `--format` (rich/yaml/json): Output format
- `--hide-sensitive`: Mask API keys (default: true)
- `--include-defaults`: Show all values including defaults

**Output**: Formatted configuration display without sensitive data

### hlpr config edit
**Purpose**: Open configuration files in editor  
**Behavior**:
- Opens config.yaml in $EDITOR or system default
- Validates after editing
- Offers to fix errors if found

### hlpr config reset
**Purpose**: Reset configuration to defaults  
**Options**:
- `--keep-api-keys`: Preserve API keys during reset
- `--backup`: Create backup before reset (default: true)

**Confirmation**: Interactive confirmation before destructive action

## Integration Contracts

### With Existing CLI Commands
All existing commands must:
1. Load configuration at startup
2. Use config values as defaults
3. Allow CLI argument override
4. Handle missing API keys gracefully

### With Guided Workflow
The guided workflow must:
1. Check for existing configuration
2. Offer to save preferences at completion
3. Integrate seamlessly with config setup

### With Document Processing
Document operations must:
1. Use configured default provider
2. Use configured default format
3. Apply configured AI parameters
4. Respect output directory preferences

## Error Contract

### Error Types
```python
class ConfigurationError(Exception):
    """Base configuration error"""
    pass

class ValidationError(ConfigurationError):
    """Configuration validation failed"""
    pass

class FileSystemError(ConfigurationError):
    """File system operation failed"""
    pass

class MigrationError(ConfigurationError):
    """Configuration migration failed"""
    pass
```

### Error Messages
- Must be actionable (tell user how to fix)
- Must be specific (which field, what value)
- Must include context (why validation failed)
- Must suggest alternatives when appropriate

## Performance Contract

### Response Time Targets
- `load_configuration()`: < 50ms
- `save_configuration()`: < 50ms
- `validate_configuration()`: < 10ms
- CLI command startup: < 100ms total

### Memory Usage
- Configuration data: < 100KB
- Manager instance: < 1MB
- No memory leaks on repeated operations

### File I/O
- Atomic operations only
- Minimal file system calls
- Efficient YAML parsing
- Proper resource cleanup