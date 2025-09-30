# Data Model: Update Config Workflow

**Date**: September 30, 2025  
**Status**: Complete  

## Core Data Models

### Configuration Schema

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from pathlib import Path
from enum import Enum

class ProviderType(str, Enum):
    """Supported AI providers"""
    LOCAL = "local"
    OPENAI = "openai" 
    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"
    GROQ = "groq"
    DEEPSEEK = "deepseek"
    GLM = "glm"
    COHERE = "cohere"
    MISTRAL = "mistral"

class OutputFormat(str, Enum):
    """Supported output formats"""
    RICH = "rich"
    TXT = "txt"
    MD = "md"
    JSON = "json"

class UserConfiguration(BaseModel):
    """User configuration preferences"""
    
    # Core provider settings
    default_provider: ProviderType = ProviderType.LOCAL
    default_format: OutputFormat = OutputFormat.RICH
    
    # AI parameters
    default_temperature: float = Field(default=0.3, ge=0.0, le=1.0)
    default_max_tokens: int = Field(default=8192, gt=0, le=32768)
    
    # File processing
    auto_save: bool = Field(default=False)
    default_output_directory: Optional[Path] = None
    
    # Advanced settings
    timeout_seconds: Optional[int] = Field(default=30, ge=0)
    
    @validator('default_output_directory', pre=True)
    def expand_path(cls, v):
        if v is None:
            return None
        return Path(v).expanduser().resolve()
    
    class Config:
        use_enum_values = True

class APICredentials(BaseModel):
    """API credentials for cloud providers"""
    
    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    glm_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None
    mistral_api_key: Optional[str] = None
    
    def get_key_for_provider(self, provider: ProviderType) -> Optional[str]:
        """Get API key for specific provider"""
        key_mapping = {
            ProviderType.OPENAI: self.openai_api_key,
            ProviderType.GOOGLE: self.google_api_key,
            ProviderType.ANTHROPIC: self.anthropic_api_key,
            ProviderType.OPENROUTER: self.openrouter_api_key,
            ProviderType.GROQ: self.groq_api_key,
            ProviderType.DEEPSEEK: self.deepseek_api_key,
            ProviderType.GLM: self.glm_api_key,
            ProviderType.COHERE: self.cohere_api_key,
            ProviderType.MISTRAL: self.mistral_api_key,
        }
        return key_mapping.get(provider)

class ConfigurationState(BaseModel):
    """Complete configuration state"""
    
    version: str = "1.0"
    config: UserConfiguration = UserConfiguration()
    credentials: APICredentials = APICredentials()
    
    def has_api_key_for_provider(self, provider: ProviderType) -> bool:
        """Check if API key exists for provider"""
        if provider == ProviderType.LOCAL:
            return True  # Local provider doesn't need API key
        return self.credentials.get_key_for_provider(provider) is not None
```

### File Structures

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ConfigurationPaths:
    """Configuration file paths"""
    
    config_dir: Path
    config_file: Path  # config.yaml
    env_file: Path     # .env
    backup_dir: Path   # backups/
    
    @classmethod
    def default(cls) -> 'ConfigurationPaths':
        """Get default configuration paths"""
        config_dir = Path.home() / ".hlpr"
        return cls(
            config_dir=config_dir,
            config_file=config_dir / "config.yaml",
            env_file=config_dir / ".env",
            backup_dir=config_dir / "backups"
        )
    
    def ensure_directories(self) -> None:
        """Create directories if they don't exist"""
        self.config_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
```

### Validation Models

```python
from pydantic import ValidationError
from typing import List, Union

class ConfigurationError(Exception):
    """Base class for configuration errors"""
    pass

class ValidationResult(BaseModel):
    """Result of configuration validation"""
    
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    
    @classmethod
    def success(cls) -> 'ValidationResult':
        return cls(is_valid=True)
    
    @classmethod
    def failure(cls, errors: List[str]) -> 'ValidationResult':
        return cls(is_valid=False, errors=errors)
    
    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

class MigrationInfo(BaseModel):
    """Information about configuration migration"""
    
    was_migrated: bool = False
    source_files: List[Path] = []
    backup_files: List[Path] = []
    migration_notes: List[str] = []
```

## Entity Relationships

```
ConfigurationState
├── UserConfiguration (1:1)
│   ├── default_provider → ProviderType
│   ├── default_format → OutputFormat
│   └── default_output_directory → Path
└── APICredentials (1:1)
    ├── openai_api_key
    ├── google_api_key
    ├── anthropic_api_key
    ├── openrouter_api_key
    ├── groq_api_key
    ├── deepseek_api_key
    ├── glm_api_key
    ├── cohere_api_key
    └── mistral_api_key

ConfigurationPaths
├── config_file → UserConfiguration (YAML)
├── env_file → APICredentials (.env)
└── backup_dir → Migration backups
```

## State Transitions

### Configuration Lifecycle

```
[No Config] → [First Run Setup] → [Active Config]
                     ↓
                [Guided Workflow] → [Config Files Created]
                     ↓
[Active Config] ← [Validation] ← [Config Loading]
       ↓
   [In Use] ↔ [Modification] → [Validation] → [Save]
       ↓
   [Reset] → [Default State] → [First Run Setup]
```

### Error Recovery States

```
[Load Config] → [Validation Error] → [Graceful Fallback]
                      ↓
              [User Choice] → [Fix Config] or [Use Defaults]
                      ↓
              [Backup Original] → [Migration/Reset]
```

## Data Constraints

### File Size Limits
- config.yaml: < 10KB (typical ~1KB)
- .env file: < 1KB
- Total configuration footprint: < 1MB

### Performance Constraints
- Configuration loading: < 50ms
- Configuration saving: < 50ms
- Memory usage: < 100KB for config data

### Security Constraints
- .env file permissions: 600 (owner read/write only)
- config.yaml permissions: 644 (owner read/write, others read)
- No sensitive data in YAML file
- API keys only in .env file

### Validation Rules
- Provider must be valid enum value
- Format must be valid enum value
- Temperature between 0.0 and 1.0
- Max tokens between 1 and 32768
- Timeout >= 0 seconds
- Paths must be absolute and exist (when specified)

## Default Values

```yaml
# Default config.yaml content
default_provider: local
default_format: rich
default_temperature: 0.3
default_max_tokens: 8192
auto_save: false
timeout_seconds: 30
```

```bash
# Default .env content (all empty initially)
OPENAI_API_KEY=
GOOGLE_API_KEY=
ANTHROPIC_API_KEY=
OPENROUTER_API_KEY=
GROQ_API_KEY=
DEEPSEEK_API_KEY=
GLM_API_KEY=
COHERE_API_KEY=
MISTRAL_API_KEY=
```