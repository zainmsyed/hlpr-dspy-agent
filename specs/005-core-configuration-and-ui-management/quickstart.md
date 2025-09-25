# Quickstart: Core Configuration and UI Management System

**Feature**: 005-core-configuration-ui  
**Date**: September 25, 2025  
**Purpose**: Step-by-step validation scenarios for configuration management system

## Prerequisites

- hlpr development environment set up
- Python 3.11+ with pytest installed  
- Write permissions to user home directory (~/.hlpr/)

## Quickstart Scenarios

### Scenario 1: Fresh Installation Configuration Loading
**Validates**: FR-001, FR-002, FR-013 (Default loading and performance)

```bash
# Step 1: Clean environment (no existing config)
rm -rf ~/.hlpr/config.json ~/.hlpr/config.backup.json

# Step 2: Start timer and load configuration
python -c "
import time
from hlpr.config.loader import ConfigLoader
from hlpr.config.validators import ConfigValidator
from hlpr.config.recovery import ConfigRecovery
from hlpr.config.ui_strings import UIStringManager

start = time.time()
loader = ConfigLoader(validator, recovery)  # Dependencies injected
result = loader.load_config()
load_time = (time.time() - start) * 1000

print(f'Load time: {load_time:.2f}ms')
print(f'Provider: {result.config.provider}')  
print(f'Format: {result.config.format}')
print(f'Chunk size: {result.config.chunk_size}')
print(f'Sources used: {[s.value for s in result.sources_used]}')
"

# Expected output:
# Load time: <100ms
# Provider: local
# Format: rich  
# Chunk size: 8192
# Sources used: ['defaults']
```

### Scenario 2: Environment Variable Override
**Validates**: FR-009, FR-017 (Override precedence and environment support)

```bash
# Step 1: Set environment variables
export HLPR_DEFAULT_PROVIDER=openai
export HLPR_DEFAULT_FORMAT=json  
export HLPR_CHUNK_SIZE=16384

# Step 2: Load configuration with overrides
python -c "
from hlpr.config.loader import ConfigLoader
# ... setup loader ...
result = loader.load_config()

print(f'Provider: {result.config.provider}')
print(f'Format: {result.config.format}')  
print(f'Chunk size: {result.config.chunk_size}')
print(f'Sources: {[s.value for s in result.sources_used]}')
"

# Expected output:
# Provider: openai
# Format: json
# Chunk size: 16384  
# Sources: ['defaults', 'environment']

# Step 3: Clean up
unset HLPR_DEFAULT_PROVIDER HLPR_DEFAULT_FORMAT HLPR_CHUNK_SIZE
```

### Scenario 3: Configuration File Creation and Loading
**Validates**: FR-017 (File-based configuration support)

```bash
# Step 1: Create user configuration directory
mkdir -p ~/.hlpr

# Step 2: Create configuration file
cat > ~/.hlpr/config.json << 'EOF'
{
  "provider": "anthropic",
  "format": "md",
  "chunk_size": 4096,
  "enable_logging": false,
  "use_color": true
}
EOF

# Step 3: Load and validate configuration
python -c "
from hlpr.config.loader import ConfigLoader
# ... setup loader ...
result = loader.load_config()

print(f'Provider: {result.config.provider}')
print(f'Format: {result.config.format}')
print(f'Chunk size: {result.config.chunk_size}')
print(f'Logging: {result.config.enable_logging}')
print(f'Sources: {[s.value for s in result.sources_used]}')
"

# Expected output:
# Provider: anthropic
# Format: md
# Chunk size: 4096
# Logging: False
# Sources: ['defaults', 'user_config']
```

### Scenario 4: Configuration Validation Errors  
**Validates**: FR-004, FR-010 (Schema validation and actionable errors)

```bash
# Step 1: Create invalid configuration
cat > ~/.hlpr/config.json << 'EOF'
{
  "provider": "invalid_provider",
  "format": "bad_format", 
  "chunk_size": -1000
}
EOF

# Step 2: Test validation with detailed errors
python -c "
from hlpr.config.validators import ConfigValidator
from hlpr.config.ui_strings import UIStringManager
import json

with open('~/.hlpr/config.json'.replace('~', str(Path.home()))) as f:
    config_data = json.load(f)

validator = ConfigValidator(ui_strings)
result = validator.validate_config(config_data)

print(f'Valid: {result.is_valid}')
print(f'Error count: {len(result.errors)}')
for error in result.errors:
    print(f'Field: {error.field}')  
    print(f'Message: {error.message}')
    print(f'Suggestion: {error.suggestion}')
    print('---')
"

# Expected output:
# Valid: False
# Error count: 3
# Field: provider
# Message: Input should be 'local', 'openai', 'anthropic', 'groq' or 'together'
# Suggestion: Use one of: local, openai, anthropic, groq, together
# ---
# Field: format  
# Message: Input should be 'rich', 'txt', 'md' or 'json'
# Suggestion: Use one of: rich, txt, md, json
# ---
# Field: chunk_size
# Message: Input should be greater than or equal to 1024
# Suggestion: Check the valid range in documentation
```

### Scenario 5: Corruption Recovery with User Data Preservation
**Validates**: FR-005, FR-006, FR-007, FR-018 (Corruption recovery and data preservation)

```bash
# Step 1: Create valid config with user preferences  
cat > ~/.hlpr/config.json << 'EOF'
{
  "provider": "openai",
  "format": "md",
  "chunk_size": 16384,
  "enable_logging": true
}
EOF

# Step 2: Create saved command templates (user data)
mkdir -p ~/.hlpr
cat > ~/.hlpr/saved_commands.json << 'EOF'
[
  {
    "id": "summary-1", 
    "command_template": "hlpr summarize document [FILE] --provider openai",
    "created": "2025-09-25T10:00:00Z"
  }
]
EOF

# Step 3: Corrupt the configuration file
echo "{ invalid json }" > ~/.hlpr/config.json

# Step 4: Test recovery with user data preservation
python -c "
from hlpr.config.recovery import ConfigRecovery
from hlpr.config.loader import ConfigLoader
import json
from pathlib import Path

# Verify saved commands exist before recovery
saved_commands_path = Path.home() / '.hlpr' / 'saved_commands.json'
original_commands = json.loads(saved_commands_path.read_text())
print(f'Original commands: {len(original_commands)}')

# Trigger recovery
loader = ConfigLoader(validator, recovery)
result = loader.load_config()

print(f'Config loaded: {result.config is not None}')
print(f'Warnings: {result.warnings}')

# Verify user data preserved  
current_commands = json.loads(saved_commands_path.read_text())
print(f'Commands preserved: {len(current_commands) == len(original_commands)}')
print(f'Command IDs match: {current_commands[0][\"id\"] == original_commands[0][\"id\"]}')

# Verify backup created
backup_path = Path.home() / '.hlpr' / 'config.backup.json'
print(f'Backup created: {backup_path.exists()}')
"

# Expected output:
# Original commands: 1
# Config loaded: True
# Warnings: ['User config invalid, falling back to defaults', 'Configuration recovered via fallback_defaults']  
# Commands preserved: True
# Command IDs match: True
# Backup created: True
```

### Scenario 6: UI Strings Validation and Reference Integrity
**Validates**: FR-003, FR-008, FR-012 (UI string externalization and integrity)

```bash
# Step 1: Test UI string loading and validation
python -c "
from hlpr.config.ui_strings import UIStringManager, UIStringKeys

# Load UI strings (should be populated from config)
strings_dict = {
    'validation.empty_path': 'Empty path: provide a valid file path',
    'validation.file_not_found': 'File not found: {path}',
    'prompts.select_provider': 'Select provider ({options}):',
    'errors.config_corrupted': 'Configuration corrupted, using defaults',
    'success.config_saved': 'Configuration saved successfully'
}

ui_manager = UIStringManager(strings_dict)

# Test string retrieval
print(f'Empty path message: {ui_manager.get(UIStringKeys.EMPTY_PATH)}')
print(f'File not found: {ui_manager.get(UIStringKeys.FILE_NOT_FOUND, path=\"/invalid\")}')

# Test missing string fallback
print(f'Missing string: {ui_manager.get(\"nonexistent.key\")}')
"

# Expected output:
# Empty path message: Empty path: provide a valid file path
# File not found: File not found: /invalid  
# Missing string: [MISSING: nonexistent.key]

# Step 2: Test integrity validation failure
python -c "
from hlpr.config.ui_strings import UIStringManager, UIStringKeys

# Missing required strings
incomplete_strings = {
    'validation.empty_path': 'Empty path message'
    # Missing other required strings
}

try:
    ui_manager = UIStringManager(incomplete_strings)
    print('ERROR: Should have failed validation')
except ValueError as e:
    print(f'Integrity check passed: {str(e)}')
"

# Expected output:
# Integrity check passed: Missing UI string: validation.file_not_found
```

### Scenario 7: Configuration Reset with Data Preservation
**Validates**: FR-007, FR-018 (Configuration reset preserves user data)

```bash
# Step 1: Create configuration with custom settings
cat > ~/.hlpr/config.json << 'EOF'
{
  "provider": "anthropic",
  "format": "json", 
  "chunk_size": 4096,
  "enable_logging": false
}
EOF

# Step 2: Create user preferences (should be preserved)
cat > ~/.hlpr/preferences.json << 'EOF'
{
  "last_used_provider": "anthropic",
  "favorite_formats": ["json", "md"],
  "recent_files": ["/home/user/doc1.md"]
}
EOF

# Step 3: Test configuration reset
python -c "
from hlpr.config.loader import ConfigLoader
from pathlib import Path
import json

# Load current preferences
prefs_path = Path.home() / '.hlpr' / 'preferences.json'
original_prefs = json.loads(prefs_path.read_text())

# Reset configuration  
loader = ConfigLoader(validator, recovery)
success = loader.reset_config(preserve_user_data=True)

print(f'Reset successful: {success}')

# Verify config reset to defaults
result = loader.load_config()
print(f'Provider reset: {result.config.provider == \"local\"}')
print(f'Format reset: {result.config.format == \"rich\"}')
print(f'Chunk size reset: {result.config.chunk_size == 8192}')

# Verify user preferences preserved
current_prefs = json.loads(prefs_path.read_text())
print(f'Preferences preserved: {current_prefs == original_prefs}')
"

# Expected output:
# Reset successful: True
# Provider reset: True
# Format reset: True  
# Chunk size reset: True
# Preferences preserved: True
```

### Scenario 8: Cross-Platform Permission Handling
**Validates**: Platform-specific permission enforcement

```bash
# Step 1: Test configuration file permissions (Linux/macOS)
python -c "
import os
import stat
from pathlib import Path

config_path = Path.home() / '.hlpr' / 'config.json'

# Create config if not exists
if not config_path.exists():
    config_path.parent.mkdir(exist_ok=True)
    config_path.write_text('{\"provider\": \"local\"}')

# Check current permissions
current_perms = oct(config_path.stat().st_mode)[-3:]
print(f'Current permissions: {current_perms}')

# On Unix systems, should be 600 (owner read/write only)
if os.name == 'posix':
    expected_perms = '600'
    if current_perms == expected_perms:
        print('✅ Secure permissions correctly set')
    else:
        print(f'⚠️  Permissions should be {expected_perms} for security')
else:
    print('ℹ️  Windows system - ACL-based permissions in use')
"

# Expected output (Linux/macOS):
# Current permissions: 600
# ✅ Secure permissions correctly set

# Expected output (Windows):  
# Current permissions: 666
# ℹ️  Windows system - ACL-based permissions in use
```

## Performance Validation

### Startup Performance Test
```bash
# Test configuration loading performance under load
python -c "
import time
from hlpr.config.loader import ConfigLoader

# Test multiple sequential loads
times = []
for i in range(10):
    start = time.time()
    result = loader.load_config()
    load_time = (time.time() - start) * 1000
    times.append(load_time)

avg_time = sum(times) / len(times)
max_time = max(times)

print(f'Average load time: {avg_time:.2f}ms')
print(f'Maximum load time: {max_time:.2f}ms')
print(f'Performance target met: {max_time < 100}')
"

# Expected output:
# Average load time: <50ms
# Maximum load time: <100ms  
# Performance target met: True
```

## Cleanup

```bash
# Remove test files
rm -f ~/.hlpr/config.json ~/.hlpr/config.backup.json
rm -f ~/.hlpr/saved_commands.json ~/.hlpr/preferences.json

# Optional: Remove test directory
# rm -rf ~/.hlpr
```

## Success Criteria

- [ ] All scenarios execute without errors
- [ ] Configuration loading completes in <100ms
- [ ] Invalid configurations trigger appropriate error messages
- [ ] Corruption recovery preserves user data
- [ ] UI strings load with referential integrity  
- [ ] Environment variables override defaults correctly
- [ ] User configuration files override environment variables
- [ ] Configuration reset preserves critical user data
- [ ] Cross-platform permissions work appropriately

## Troubleshooting

### Common Issues

**Permission Denied**: Ensure write access to ~/.hlpr/ directory
```bash
chmod 755 ~/.hlpr
```

**Import Errors**: Ensure hlpr package is in Python path
```bash
export PYTHONPATH=/path/to/hlpr/src:$PYTHONPATH
```

**JSON Parse Errors**: Validate JSON syntax in configuration files
```bash
python -m json.tool ~/.hlpr/config.json
```

---

**Quickstart Status**: Complete ✅  
**Validation**: Ready for automated testing  
**Integration**: Compatible with existing hlpr CLI workflow