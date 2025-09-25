# Data Model: Core Configuration and UI Management System

**Feature**: 005-core-configuration-ui  
**Date**: September 25, 2025  
**Source**: Derived from feature spec functional requirements

## Core Entities

### PlatformConfig
**Purpose**: Central configuration container with immutable defaults and validation
**Location**: `src/hlpr/config/platform.py`

```python
@dataclass(frozen=True)
class PlatformDefaults:
    """Immutable platform constants - compile-time defaults"""
    
    # Provider defaults (FR-001)
    default_provider: str = "local"
    supported_providers: tuple[str, ...] = ("local", "openai", "anthropic", "groq", "together")
    
    # Format defaults (FR-002)
    default_format: str = "rich"  
    supported_formats: tuple[str, ...] = ("rich", "txt", "md", "json")
    
    # Chunk size limits (FR-011)
    default_chunk_size: int = 8192
    min_chunk_size: int = 1024
    max_chunk_size: int = 32768
    
    # Performance constraints (FR-013)
    config_load_timeout_ms: int = 100
    validation_timeout_ms: int = 10
    
    # File paths
    config_dir_name: str = ".hlpr"
    config_filename: str = "config.json"
    backup_filename: str = "config.backup.json"

class PlatformConfig(BaseModel):
    """Runtime configuration with validation - loaded from files/env"""
    
    # User preferences (FR-009)
    provider: str = Field(default=PlatformDefaults.default_provider)
    format: str = Field(default=PlatformDefaults.default_format)
    chunk_size: int = Field(default=PlatformDefaults.default_chunk_size)
    
    # System settings
    enable_logging: bool = Field(default=True)
    log_level: str = Field(default="INFO")
    
    # UI preferences  
    use_color: bool = Field(default=True)
    show_progress: bool = Field(default=True)
    
    @field_validator('provider')
    def validate_provider(cls, v):
        if v not in PlatformDefaults.supported_providers:
            raise ValueError(f"Unsupported provider: {v}")
        return v
        
    @field_validator('format')
    def validate_format(cls, v):
        if v not in PlatformDefaults.supported_formats:
            raise ValueError(f"Unsupported format: {v}")
        return v
        
    @field_validator('chunk_size')
    def validate_chunk_size(cls, v):
        if not (PlatformDefaults.min_chunk_size <= v <= PlatformDefaults.max_chunk_size):
            raise ValueError(f"Chunk size must be between {PlatformDefaults.min_chunk_size} and {PlatformDefaults.max_chunk_size}")
        return v
```

**Relationships**: Used by ConfigLoader, validated by ConfigValidator

---

### UIStringManager
**Purpose**: Externalized string resources with referential integrity (FR-003, FR-008, FR-012)
**Location**: `src/hlpr/config/ui_strings.py` (extended)

```python
@dataclass(frozen=True)
class UIStringKeys:
    """String key constants for referential integrity"""
    # Validation messages
    EMPTY_PATH: str = "validation.empty_path"
    FILE_NOT_FOUND: str = "validation.file_not_found"
    UNSUPPORTED_PROVIDER: str = "validation.unsupported_provider"
    
    # CLI prompts
    SELECT_PROVIDER: str = "prompts.select_provider"
    SELECT_FORMAT: str = "prompts.select_format"
    CONFIRM_RESET: str = "prompts.confirm_reset"
    
    # Error messages
    CONFIG_CORRUPTED: str = "errors.config_corrupted"
    PERMISSION_DENIED: str = "errors.permission_denied"
    
    # Success messages
    CONFIG_RESET_SUCCESS: str = "success.config_reset"
    CONFIG_SAVED: str = "success.config_saved"

class UIStringManager:
    """Manages UI strings with validation and fallback"""
    
    def __init__(self, strings_dict: dict[str, str]):
        self._strings = strings_dict
        self._validate_integrity()
    
    def get(self, key: str, **format_args) -> str:
        """Get string with fallback and formatting"""
        template = self._strings.get(key, f"[MISSING: {key}]")
        return template.format(**format_args) if format_args else template
    
    def _validate_integrity(self) -> None:
        """Validate all string keys exist (FR-008)"""
        for key_name in UIStringKeys.__annotations__:
            key_value = getattr(UIStringKeys, key_name)
            if key_value not in self._strings:
                raise ValueError(f"Missing UI string: {key_value}")
```

**Relationships**: Used by CLI modules, validated during initialization

---

### ConfigValidator  
**Purpose**: Schema validation with structured error reporting (FR-004, FR-010)
**Location**: `src/hlpr/config/validators.py`

```python
class ValidationResult(BaseModel):
    """Structured validation result"""
    is_valid: bool
    errors: list[ValidationError] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

class ValidationError(BaseModel):
    """Detailed validation error"""
    field: str
    value: Any
    message: str
    suggestion: str | None = None

class ConfigValidator:
    """Configuration validation engine"""
    
    def __init__(self, ui_strings: UIStringManager):
        self._ui_strings = ui_strings
    
    def validate_config(self, config_data: dict) -> ValidationResult:
        """Validate configuration with actionable errors (FR-010)"""
        result = ValidationResult(is_valid=True)
        
        try:
            # Pydantic validation
            PlatformConfig.model_validate(config_data)
        except ValidationError as e:
            result.is_valid = False
            for error in e.errors():
                result.errors.append(ValidationError(
                    field=error['loc'][0] if error['loc'] else 'root',
                    value=error['input'],
                    message=error['msg'],
                    suggestion=self._get_suggestion(error)
                ))
        
        return result
    
    def _get_suggestion(self, error: dict) -> str | None:
        """Generate actionable suggestions for errors"""
        if error['type'] == 'enum':
            return f"Use one of: {', '.join(error['ctx']['enum_values'])}"
        elif error['type'] == 'value_error':
            return "Check the valid range in documentation"
        return None
```

**Relationships**: Uses UIStringManager for messages, validates PlatformConfig

---

### ConfigRecovery
**Purpose**: Corruption detection and atomic recovery (FR-005, FR-006, FR-007)
**Location**: `src/hlpr/config/recovery.py`

```python
class RecoveryAction(Enum):
    """Types of recovery actions"""
    FALLBACK_TO_DEFAULTS = "fallback_defaults"
    RESTORE_FROM_BACKUP = "restore_backup"
    CREATE_NEW_CONFIG = "create_new"

class RecoveryResult(BaseModel):
    """Recovery operation result"""
    success: bool
    action_taken: RecoveryAction
    backup_created: bool = False
    errors_fixed: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)

class ConfigRecovery:
    """Configuration corruption recovery system"""
    
    def __init__(self, config_path: Path, backup_path: Path, logger: Logger):
        self._config_path = config_path
        self._backup_path = backup_path
        self._logger = logger
    
    def detect_corruption(self, config_data: dict) -> bool:
        """Detect configuration corruption"""
        try:
            PlatformConfig.model_validate(config_data)
            return False
        except ValidationError:
            return True
    
    def recover_config(self, preserve_user_data: bool = True) -> RecoveryResult:
        """Recover from corruption with user data preservation (FR-007)"""
        result = RecoveryResult(success=False, action_taken=RecoveryAction.FALLBACK_TO_DEFAULTS)
        
        try:
            # Create backup if possible
            if self._config_path.exists():
                result.backup_created = self._create_backup()
            
            # Try to preserve user data
            user_data = {}
            if preserve_user_data and self._backup_path.exists():
                user_data = self._extract_user_data()
            
            # Create new config with preserved data
            new_config = PlatformConfig()
            if user_data:
                # Merge user preferences safely
                new_config = self._merge_user_data(new_config, user_data)
            
            # Write atomic config
            self._write_atomic_config(new_config.model_dump())
            
            result.success = True
            self._logger.info(f"Configuration recovered: {result.action_taken}")
            
        except Exception as e:
            self._logger.error(f"Recovery failed: {e}")
        
        return result
    
    def _create_backup(self) -> bool:
        """Create atomic backup of current config"""
        try:
            shutil.copy2(self._config_path, self._backup_path)
            return True
        except Exception:
            return False
    
    def _write_atomic_config(self, config_data: dict) -> None:
        """Write configuration atomically to prevent corruption"""
        temp_path = self._config_path.with_suffix('.tmp')
        try:
            with temp_path.open('w') as f:
                json.dump(config_data, f, indent=2)
            temp_path.replace(self._config_path)
        finally:
            if temp_path.exists():
                temp_path.unlink()
```

**Relationships**: Uses PlatformConfig for validation, creates backups, preserves user data

---

### ConfigLoader
**Purpose**: Unified loader with override precedence (FR-009, FR-017)
**Location**: `src/hlpr/config/loader.py`

```python
class ConfigSource(Enum):
    """Configuration sources in precedence order"""
    USER_CONFIG = "user_config"
    ENVIRONMENT = "environment" 
    SYSTEM_DEFAULTS = "defaults"

class LoadResult(BaseModel):
    """Configuration loading result"""
    config: PlatformConfig
    sources_used: list[ConfigSource]
    load_time_ms: float
    warnings: list[str] = Field(default_factory=list)

class ConfigLoader:
    """Unified configuration loader with precedence handling"""
    
    def __init__(self, validator: ConfigValidator, recovery: ConfigRecovery):
        self._validator = validator
        self._recovery = recovery
    
    def load_config(self) -> LoadResult:
        """Load configuration with override precedence (FR-009)"""
        start_time = time.time()
        sources_used = []
        warnings = []
        
        # Load in precedence order: defaults < environment < user config
        config_data = {}
        
        # 1. System defaults (always present)
        config_data.update(PlatformDefaults().__dict__)
        sources_used.append(ConfigSource.SYSTEM_DEFAULTS)
        
        # 2. Environment variables (FR-017)
        env_config = self._load_from_environment()
        if env_config:
            config_data.update(env_config)
            sources_used.append(ConfigSource.ENVIRONMENT)
        
        # 3. User configuration file (FR-017)
        user_config = self._load_from_file()
        if user_config:
            if self._validator.validate_config(user_config).is_valid:
                config_data.update(user_config)
                sources_used.append(ConfigSource.USER_CONFIG)
            else:
                warnings.append("User config invalid, falling back to defaults")
                recovery_result = self._recovery.recover_config()
                if recovery_result.success:
                    warnings.append(f"Configuration recovered via {recovery_result.action_taken}")
        
        # Validate final configuration
        final_config = PlatformConfig.model_validate(config_data)
        
        load_time_ms = (time.time() - start_time) * 1000
        
        return LoadResult(
            config=final_config,
            sources_used=sources_used,
            load_time_ms=load_time_ms,
            warnings=warnings
        )
    
    def _load_from_environment(self) -> dict:
        """Load configuration from environment variables"""
        env_config = {}
        
        if provider := os.getenv('HLPR_DEFAULT_PROVIDER'):
            env_config['provider'] = provider
        if format_val := os.getenv('HLPR_DEFAULT_FORMAT'):
            env_config['format'] = format_val
        if chunk_size := os.getenv('HLPR_CHUNK_SIZE'):
            try:
                env_config['chunk_size'] = int(chunk_size)
            except ValueError:
                pass  # Ignore invalid values
        
        return env_config
    
    def _load_from_file(self) -> dict | None:
        """Load configuration from user config file"""
        config_path = Path.home() / PlatformDefaults.config_dir_name / PlatformDefaults.config_filename
        
        if not config_path.exists():
            return None
        
        try:
            with config_path.open() as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
```

**Relationships**: Uses ConfigValidator and ConfigRecovery, produces PlatformConfig

---

## Entity Relationships

```
PlatformDefaults (immutable) ←─── PlatformConfig (validated)
                ↓                        ↓
           ConfigLoader ──────→ ConfigValidator ──────→ ValidationResult
                ↓                        ↓
           RecoveryResult ←──── ConfigRecovery
                                        ↑
                               UIStringManager
```

## State Transitions

### Configuration Loading States
1. **Initial**: System starts, no config loaded
2. **Loading**: Reading from sources (file, env, defaults)  
3. **Validating**: Schema validation and integrity checks
4. **Valid**: Configuration successfully loaded and validated
5. **Corrupted**: Validation failed, recovery needed
6. **Recovering**: Corruption recovery in progress
7. **Recovered**: Fallback configuration active with user data preserved

### Recovery States
1. **Healthy**: Configuration valid and accessible
2. **Corrupted**: Corruption detected, backup needed
3. **Backed Up**: Original config preserved for data extraction
4. **Fallback**: Using system defaults with preserved user data
5. **Restored**: New valid configuration written atomically

## Validation Rules

### Provider Validation (FR-001)
- Must be one of: "local", "openai", "anthropic", "groq", "together"
- Case-sensitive validation
- No custom providers allowed in this version

### Format Validation (FR-002)  
- Must be one of: "rich", "txt", "md", "json"
- Case-sensitive validation
- Format capabilities checked against terminal capabilities

### Chunk Size Validation (FR-011)
- Range: 1024 ≤ chunk_size ≤ 32768
- Must be positive integer
- Provider-specific limits may apply (future enhancement)

### Performance Validation (FR-013)
- Configuration loading: <100ms timeout
- Validation processing: <10ms per config item
- File I/O operations: <50ms per file

---

**Status**: Complete ✅  
**Next**: Contract generation and quickstart scenarios