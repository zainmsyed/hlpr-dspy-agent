# Configuration Management System Contracts

**Feature**: 005-core-configuration-ui  
**Date**: September 25, 2025  
**Purpose**: API contracts for configuration management system components

## Contract: PlatformConfig Loading

### ConfigLoader.load_config()

**Input**: None (reads from system)  
**Output**: LoadResult  
**Performance**: <100ms execution time

```python
# SUCCESS Case
def test_config_loader_success():
    # Given: Valid configuration sources exist
    # When: load_config() is called
    # Then: Returns LoadResult with valid PlatformConfig
    result = loader.load_config()
    assert isinstance(result, LoadResult)
    assert isinstance(result.config, PlatformConfig)
    assert result.load_time_ms < 100
    assert ConfigSource.SYSTEM_DEFAULTS in result.sources_used

# CORRUPTION Case  
def test_config_loader_corruption_recovery():
    # Given: Corrupted user configuration file
    # When: load_config() is called
    # Then: Recovers gracefully with fallback
    result = loader.load_config()
    assert result.config is not None
    assert len(result.warnings) > 0
    assert "recovered" in result.warnings[0].lower()
```

---

## Contract: Configuration Validation

### ConfigValidator.validate_config()

**Input**: dict (configuration data)  
**Output**: ValidationResult  
**Performance**: <10ms per validation

```python  
# VALID Case
def test_validator_valid_config():
    config_data = {
        "provider": "local",
        "format": "rich", 
        "chunk_size": 8192
    }
    result = validator.validate_config(config_data)
    assert result.is_valid is True
    assert len(result.errors) == 0

# INVALID Case - Unsupported Provider
def test_validator_invalid_provider():
    config_data = {"provider": "unsupported"}
    result = validator.validate_config(config_data)
    assert result.is_valid is False
    assert len(result.errors) == 1
    assert result.errors[0].field == "provider"
    assert "unsupported" in result.errors[0].message.lower()
    assert result.errors[0].suggestion is not None

# INVALID Case - Chunk Size Out of Range
def test_validator_invalid_chunk_size():
    config_data = {"chunk_size": 50000}  # Exceeds max
    result = validator.validate_config(config_data)
    assert result.is_valid is False
    assert result.errors[0].field == "chunk_size"
    assert "range" in result.errors[0].suggestion.lower()
```

---

## Contract: Configuration Recovery

### ConfigRecovery.recover_config()

**Input**: preserve_user_data: bool = True  
**Output**: RecoveryResult  
**Side Effects**: Creates backup, writes new config file

```python
# RECOVERY Success
def test_recovery_success_with_user_data():
    # Given: Corrupted config exists with recoverable user data
    # When: recover_config(preserve_user_data=True) is called
    # Then: Creates backup and preserves user preferences
    result = recovery.recover_config(preserve_user_data=True)
    assert result.success is True
    assert result.backup_created is True
    assert result.action_taken == RecoveryAction.FALLBACK_TO_DEFAULTS
    assert result.timestamp is not None

# RECOVERY Failure
def test_recovery_disk_full():
    # Given: Insufficient disk space for backup
    # When: recover_config() is called  
    # Then: Fails gracefully without corrupting existing data
    result = recovery.recover_config()
    assert result.success is False
    # Original config should remain untouched
```

---

## Contract: UI String Management

### UIStringManager.get()

**Input**: key: str, **format_args  
**Output**: str (formatted string)  
**Behavior**: Returns fallback for missing keys

```python
# SUCCESS Case
def test_ui_strings_valid_key():
    string_manager = UIStringManager(valid_strings_dict)
    result = string_manager.get(UIStringKeys.EMPTY_PATH)
    assert isinstance(result, str)
    assert len(result) > 0
    assert "[MISSING:" not in result

# FORMATTING Case
def test_ui_strings_formatting():
    result = string_manager.get(
        UIStringKeys.FILE_NOT_FOUND, 
        path="/invalid/path"
    )
    assert "/invalid/path" in result

# MISSING Key Case
def test_ui_strings_missing_key():
    result = string_manager.get("nonexistent.key")
    assert "[MISSING: nonexistent.key]" in result
```

---

## Contract: Platform Constants

### PlatformDefaults Access

**Input**: None (class attributes)  
**Output**: Immutable values  
**Constraint**: No circular imports

```python
# CONSTANTS Access
def test_platform_defaults_immutable():
    # Given: PlatformDefaults is imported
    # When: Accessing default values
    # Then: Values are consistent and immutable
    assert PlatformDefaults.default_provider == "local"
    assert "local" in PlatformDefaults.supported_providers
    assert PlatformDefaults.default_chunk_size == 8192
    
    # Ensure immutability (frozen dataclass)
    with pytest.raises(AttributeError):
        PlatformDefaults.default_provider = "changed"

# IMPORT Safety
def test_no_circular_imports():
    # Given: Platform constants module
    # When: Imported by any hlpr module
    # Then: No circular import errors occur
    from hlpr.config.platform import PlatformDefaults
    from hlpr.document.summarizer import DocumentSummarizer
    # Should not raise ImportError
```

---

## Contract: Configuration Reset

### ConfigLoader.reset_config()

**Input**: preserve_user_data: bool = True  
**Output**: bool (success status)  
**Side Effects**: Preserves command templates and preferences

```python
# RESET Success
def test_config_reset_preserves_user_data():
    # Given: Existing config with user preferences and command templates
    saved_commands = load_saved_commands()  # User's saved commands
    # When: reset_config(preserve_user_data=True) is called
    success = loader.reset_config(preserve_user_data=True)
    # Then: Configuration is reset but user data preserved
    assert success is True
    assert load_saved_commands() == saved_commands
    
# RESET Clean
def test_config_reset_clean():
    # Given: Corrupted configuration
    # When: reset_config(preserve_user_data=False) is called
    success = loader.reset_config(preserve_user_data=False)
    # Then: Complete clean reset to factory defaults
    assert success is True
    new_config = loader.load_config().config
    assert new_config.provider == PlatformDefaults.default_provider
```

---

## Contract: Environment Override

### Environment Variable Processing

**Input**: Environment variables (HLPR_*)  
**Output**: Configuration overrides  
**Precedence**: User config > Environment > Defaults

```python
# ENVIRONMENT Override
def test_environment_override_precedence():
    # Given: Environment variable set
    os.environ["HLPR_DEFAULT_PROVIDER"] = "openai"
    # When: Configuration is loaded
    result = loader.load_config()
    # Then: Environment value overrides default
    assert result.config.provider == "openai"
    assert ConfigSource.ENVIRONMENT in result.sources_used

# USER Config Priority  
def test_user_config_overrides_environment():
    # Given: Both environment and user config set different values
    os.environ["HLPR_DEFAULT_PROVIDER"] = "openai"
    # And: User config file contains "provider": "anthropic"
    result = loader.load_config()
    # Then: User config takes precedence
    assert result.config.provider == "anthropic"
    assert ConfigSource.USER_CONFIG in result.sources_used
```

---

## Performance Contracts

### Startup Time Constraints

```python
def test_configuration_startup_performance():
    # Given: Normal system conditions
    # When: Full configuration loading occurs
    start_time = time.time()
    result = loader.load_config()
    load_time = (time.time() - start_time) * 1000
    # Then: Completes within performance constraints
    assert load_time < 100  # FR-013: <100ms
    assert result.load_time_ms < 100

def test_validation_performance():
    # Given: Typical configuration data
    config_data = generate_typical_config()
    # When: Validation is performed
    start_time = time.time()
    result = validator.validate_config(config_data)
    validation_time = (time.time() - start_time) * 1000
    # Then: Completes within performance constraints  
    assert validation_time < 10  # FR-013: <10ms per item
```

---

**Contract Status**: Complete ✅  
**Test Implementation**: Required for Phase 3  
**API Stability**: Backwards compatible with existing config.py