# Quickstart Validation: Update Config Workflow

**Date**: September 30, 2025  
**Status**: Complete  

## Test Environment Setup

### Prerequisites
- Clean hlpr installation 
- No existing ~/.hlpr/ directory
- Python 3.11+ with hlpr dependencies
- Terminal with Rich support

### Test Data Files
Create test document for validation:
```bash
mkdir -p /tmp/hlpr-test
echo "# Test Document\nThis is a test document for configuration validation." > /tmp/hlpr-test/sample.md
```

## User Story Validation Scenarios

### Scenario 1: First-Time User Setup
**Story**: New user runs hlpr for first time and sets up preferences

**Steps**:
1. Ensure no ~/.hlpr/ directory exists
2. Run: `hlpr summarize document /tmp/hlpr-test/sample.md`
3. System should prompt for configuration setup
4. Follow guided setup with default local provider
5. Verify command completes successfully
6. Check ~/.hlpr/config.yaml created with chosen settings

**Expected Results**:
- Guided configuration prompt appears
- User can complete setup in <60 seconds
- Configuration files created with correct permissions
- Subsequent commands use saved preferences
- No API key required for local provider

**Validation Commands**:
```bash
# Verify config files exist
ls -la ~/.hlpr/
test -f ~/.hlpr/config.yaml
test -f ~/.hlpr/.env

# Check file permissions
stat -c "%a" ~/.hlpr/.env | grep "600"
stat -c "%a" ~/.hlpr/config.yaml | grep "644"

# Verify config content
hlpr config show
```

### Scenario 2: Returning User Experience  
**Story**: User with saved configuration runs commands without prompts

**Steps**:
1. Complete Scenario 1 first
2. Run: `hlpr summarize document /tmp/hlpr-test/sample.md`
3. Verify no configuration prompts appear
4. Command should use saved preferences
5. Output format should match configured preference

**Expected Results**:
- No setup prompts for subsequent runs
- Configuration loaded in <100ms
- Commands use saved provider/format preferences
- User can override with CLI arguments if needed

**Validation Commands**:
```bash
# Test default behavior
time hlpr config show  # Should be < 100ms

# Test CLI override
hlpr summarize document /tmp/hlpr-test/sample.md --format json
```

### Scenario 3: Configuration Management
**Story**: User wants to change preferences after initial setup

**Steps**:
1. Run: `hlpr config setup` 
2. Change provider from local to openai
3. System should prompt for API key
4. Skip API key setup (test graceful handling)
5. Save configuration
6. Verify changes persisted

**Expected Results**:
- Configuration wizard shows current values as defaults
- Changes are saved to config files
- Missing API key handled gracefully
- Clear guidance provided for API key setup

**Validation Commands**:
```bash
# Show current config
hlpr config show

# Test API key error handling
hlpr summarize document /tmp/hlpr-test/sample.md --provider openai
# Should show clear error about missing API key
```

### Scenario 4: Error Recovery
**Story**: User has corrupted configuration files

**Steps**:
1. Corrupt the config file: `echo "invalid: yaml: content" > ~/.hlpr/config.yaml`
2. Run: `hlpr config show`
3. System should detect corruption and offer recovery
4. Choose to use defaults and continue
5. Verify functionality restored

**Expected Results**:
- Corruption detected and reported clearly
- Graceful fallback to defaults offered
- User can choose to fix or continue
- System remains functional with defaults

**Validation Commands**:
```bash
# Corrupt config
echo "invalid: yaml: }" > ~/.hlpr/config.yaml

# Test recovery
hlpr config validate
hlpr config show  # Should work with defaults

# Test auto-fix
hlpr config validate --fix
```

### Scenario 5: API Key Management
**Story**: User adds cloud provider API key

**Steps**:
1. Run: `hlpr config setup`
2. Select openai provider
3. Enter valid-looking API key: `sk-test123456789`
4. Save configuration
5. Verify API key stored securely
6. Test provider switching

**Expected Results**:
- API key stored in .env file with 600 permissions
- Key not visible in config.yaml file
- API key masked in display commands
- Provider switching works correctly

**Validation Commands**:
```bash
# Check .env file permissions and content
ls -la ~/.hlpr/.env
stat -c "%a" ~/.hlpr/.env

# Verify key is masked in display
hlpr config show
hlpr config show --hide-sensitive

# Test provider functionality
hlpr config show --key default_provider
```

### Scenario 6: Configuration Reset
**Story**: User wants to reset to factory defaults

**Steps**:
1. Set up custom configuration (non-default values)
2. Run: `hlpr config reset`
3. Confirm reset when prompted
4. Verify configuration returns to defaults
5. Check backup was created

**Expected Results**:
- Reset requires confirmation
- Backup created before reset
- All values return to defaults
- API keys removed (unless --keep-api-keys used)

**Validation Commands**:
```bash
# Setup custom config first
hlpr config setup --provider openai --format json --non-interactive

# Test reset
hlpr config reset --backup
ls ~/.hlpr/backups/

# Verify defaults restored
hlpr config show
```

## Performance Validation

### Configuration Loading Speed
**Target**: <100ms for all configuration operations

**Test**:
```bash
# Time configuration loading
time hlpr config show > /dev/null

# Time configuration in command startup
time hlpr summarize document /tmp/hlpr-test/sample.md --help

# Test with various config file sizes
# (Generate larger configs and test performance)
```

**Expected**: All operations complete within 100ms

### Memory Usage
**Target**: <1MB memory footprint for configuration subsystem

**Test**:
```bash
# Monitor memory during config operations
/usr/bin/time -v hlpr config show
/usr/bin/time -v hlpr config setup --non-interactive
```

**Expected**: Memory usage remains minimal

## Integration Validation

### CLI Integration
**Test**: All existing commands respect configuration

```bash
# Test document summarization uses config defaults
hlpr summarize document /tmp/hlpr-test/sample.md

# Test guided workflow integration  
hlpr summarize guided --simulate-work

# Test API endpoints respect configuration
# (If API module exists)
```

### Environment Variable Override
**Test**: Environment variables override config file values

```bash
# Set config to local provider
hlpr config setup --provider local --non-interactive

# Override with environment variable
HLPR_DEFAULT_PROVIDER=openai hlpr config show --key default_provider
# Should show "openai" not "local"
```

## Error Scenarios

### File System Errors
**Test**: Handle permission and disk space issues

```bash
# Test permission errors
chmod 000 ~/.hlpr/config.yaml
hlpr config show  # Should fall back to defaults

# Test directory creation
rm -rf ~/.hlpr/
hlpr config setup --non-interactive  # Should create directory
```

### Validation Errors  
**Test**: Handle invalid configuration values

```bash
# Test invalid values
echo "default_temperature: 5.0" >> ~/.hlpr/config.yaml
hlpr config validate  # Should report error

# Test invalid provider
echo "default_provider: invalid" >> ~/.hlpr/config.yaml  
hlpr config validate  # Should report error
```

## Success Criteria Checklist

### Functional Requirements
- [ ] FR-001: Guided setup on first run ✓
- [ ] FR-002: Preferences persist between sessions ✓
- [ ] FR-003: Dedicated config command ✓
- [ ] FR-004: Secure API key storage ✓
- [ ] FR-005: Clear placeholder examples ✓
- [ ] FR-006: Validation with graceful fallback ✓
- [ ] FR-007: Config defaults with CLI override ✓
- [ ] FR-008: Config display without sensitive data ✓
- [ ] FR-009: Configuration reset command ✓
- [ ] FR-010: Missing API key detection and guidance ✓
- [ ] FR-011: Restricted file permissions ✓
- [ ] FR-012: Direct file editing support ✓

### Non-Functional Requirements
- [ ] NFR-001: <100ms configuration loading ✓
- [ ] NFR-002: <100ms configuration saving ✓
- [ ] NFR-003: <1MB configuration files ✓

### User Experience Goals
- [ ] Zero configuration errors for default workflows
- [ ] <60 second guided setup completion
- [ ] Clear, actionable error messages
- [ ] Intuitive file format for manual editing
- [ ] Seamless integration with existing commands

## Troubleshooting Guide

### Common Issues and Solutions

**Config files not created**:
```bash
# Check directory permissions
ls -la ~/.hlpr/
# Manually create if needed
mkdir -p ~/.hlpr && chmod 755 ~/.hlpr
```

**API key not working**:
```bash
# Verify .env file format
cat ~/.hlpr/.env
# Check file permissions
stat -c "%a" ~/.hlpr/.env
```

**Performance issues**:
```bash
# Check config file size
ls -lh ~/.hlpr/config.yaml
# Validate configuration
hlpr config validate
```

**Validation errors**:
```bash
# Get detailed error info
hlpr config validate --format json
# Auto-fix common issues
hlpr config validate --fix
```