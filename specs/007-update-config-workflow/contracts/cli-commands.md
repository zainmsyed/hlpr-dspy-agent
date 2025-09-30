# CLI Commands API Contract

**Date**: September 30, 2025  
**Status**: Complete  

## Command Structure

### Base Command
```bash
hlpr config [SUBCOMMAND] [OPTIONS]
```

## Subcommands Specification

### setup
**Purpose**: Interactive configuration setup wizard  
**Usage**: `hlpr config setup [OPTIONS]`

**Options**:
- `--provider TEXT`: Pre-select provider (local|openai|google|anthropic|openrouter|groq|deepseek|glm|cohere|mistral)
- `--format TEXT`: Pre-select format (rich|txt|md|json)
- `--non-interactive`: Skip prompts, use provided options or defaults
- `--force`: Overwrite existing configuration without confirmation

**Interactive Flow**:
1. Welcome message and current status
2. Provider selection with help text
3. Format selection with examples
4. Basic settings (temperature, auto-save)
5. API key setup (if cloud provider selected)
6. Confirmation and save

**Exit Codes**:
- 0: Configuration saved successfully
- 1: User cancelled during setup
- 2: Invalid options provided
- 3: File system error (permissions, disk space)

**Output Example**:
```
┌─ Configuration Setup ─┐
│ Current: local, rich   │
└────────────────────────┘

✓ Provider: local
✓ Format: rich  
✓ Temperature: 0.3
✓ Auto-save: disabled

Configuration saved to ~/.hlpr/config.yaml
```

### show
**Purpose**: Display current configuration values  
**Usage**: `hlpr config show [OPTIONS]`

**Options**:
- `--format TEXT`: Output format (rich|yaml|json) [default: rich]
- `--hide-sensitive/--show-sensitive`: Hide/show API keys [default: hide]
- `--include-defaults`: Show all values including defaults [default: false]
- `--key TEXT`: Show specific configuration key only

**Output Examples**:

**Rich format**:
```
┌─ Configuration ─┐
│ Provider: local  │
│ Format: rich     │
│ Temperature: 0.3 │
│ Auto-save: No    │
└──────────────────┘

┌─ API Keys ─┐
│ OpenAI: ●●●● │
│ Other: None  │
└──────────────┘
```

**YAML format**:
```yaml
default_provider: local
default_format: rich
default_temperature: 0.3
auto_save: false
# API keys: [HIDDEN]
```

**JSON format**:
```json
{
  "default_provider": "local",
  "default_format": "rich", 
  "default_temperature": 0.3,
  "auto_save": false,
  "api_keys_configured": ["openai"]
}
```

### edit
**Purpose**: Open configuration files in text editor  
**Usage**: `hlpr config edit [OPTIONS]`

**Options**:
- `--editor TEXT`: Specify editor command [default: $EDITOR or system default]
- `--file TEXT`: Edit specific file (config|env) [default: config]
- `--validate`: Validate after editing [default: true]

**Behavior**:
1. Open config.yaml in specified editor
2. Wait for editor to close
3. Validate configuration
4. Report validation results
5. Offer to fix errors if found

**Post-Edit Validation**:
```
✓ Configuration validated successfully
⚠ Warning: temperature value high (0.9), consider 0.3-0.7 range
```

### reset
**Purpose**: Reset configuration to factory defaults  
**Usage**: `hlpr config reset [OPTIONS]`

**Options**:
- `--keep-api-keys`: Preserve API keys during reset [default: false]
- `--backup/--no-backup`: Create backup before reset [default: true]
- `--force`: Skip confirmation prompt [default: false]

**Interactive Confirmation**:
```
⚠ This will reset your configuration to defaults.
  
Current configuration will be backed up to:
~/.hlpr/backups/config-2025-09-30-14-30-15.yaml

Keep API keys? [y/N]: n
Proceed with reset? [y/N]: y

✓ Configuration reset to defaults
✓ Backup saved: ~/.hlpr/backups/config-2025-09-30-14-30-15.yaml
```

### validate
**Purpose**: Validate current configuration without changes  
**Usage**: `hlpr config validate [OPTIONS]`

**Options**:
- `--fix`: Attempt to fix validation errors automatically
- `--format TEXT`: Output format for results (rich|json) [default: rich]

**Output Examples**:

**Valid configuration**:
```
✓ Configuration validation passed
✓ All API keys properly formatted
✓ File permissions correct
```

**Invalid configuration**:
```
✗ Configuration validation failed

Errors:
• temperature: 1.5 is greater than maximum 1.0
• default_provider: 'invalid' is not a valid provider

Warnings:  
• ~/.hlpr/.env has permissions 644, should be 600

Run 'hlpr config edit' to fix errors
```

## Global Integration

### Environment Variable Override
All configuration values can be overridden by environment variables:
```bash
HLPR_DEFAULT_PROVIDER=openai hlpr summarize document.pdf
HLPR_DEFAULT_FORMAT=json hlpr config show
```

**Variable Naming**: `HLPR_` + uppercase field name  
**Precedence**: CLI args > Environment vars > Config file > Defaults

### Configuration Loading
All hlpr commands must:
1. Load configuration at startup (< 100ms)
2. Apply environment variable overrides  
3. Use config values as defaults for CLI options
4. Handle configuration errors gracefully

**Error Handling During Load**:
```
⚠ Configuration file corrupted, using defaults
  Run 'hlpr config validate --fix' to repair

[Command continues with defaults]
```

### API Key Integration
Commands requiring API keys must:
1. Check configuration for required key
2. Provide clear error if missing
3. Guide user to configuration setup

**Missing API Key Error**:
```
✗ OpenAI API key required for openai provider

Set your API key:
  hlpr config setup          # Interactive setup
  hlpr config edit           # Manual editing

Get API key: https://platform.openai.com/api-keys
```

## Command Chaining Support

### Non-Interactive Mode
All commands support `--non-interactive` for scripting:
```bash
# Batch setup
hlpr config setup --provider local --format json --non-interactive

# Validation in CI
hlpr config validate --format json | jq '.errors | length'
```

### Output Parsing
JSON output mode supports programmatic usage:
```bash
# Get current provider
hlpr config show --key default_provider --format json | jq -r '.default_provider'

# Check if API key exists
hlpr config show --format json | jq '.api_keys_configured | contains(["openai"])'
```

## Error Messages Contract

### User-Friendly Errors
All error messages must:
- Explain what went wrong in plain language
- Suggest specific actions to fix the problem
- Include relevant commands or file paths
- Use consistent formatting with Rich styling

### Error Categories

**File System Errors**:
```
✗ Cannot write to ~/.hlpr/config.yaml
  
  Permission denied. Try:
  chmod 755 ~/.hlpr
  chmod 644 ~/.hlpr/config.yaml
```

**Validation Errors**:
```
✗ Invalid configuration value
  
  temperature: "high" is not a number
  Expected: number between 0.0 and 1.0
  
  Fix: hlpr config setup
```

**API Key Errors**:
```
✗ Invalid API key format
  
  OpenAI keys start with 'sk-'
  Get your key: https://platform.openai.com/api-keys
  
  Fix: hlpr config edit
```

## Help System Integration

### Command Help
Each command provides comprehensive help:
```bash
hlpr config setup --help
hlpr config show --help  
hlpr config edit --help
hlpr config reset --help
```

### Context-Sensitive Help
Commands show relevant help based on current state:
- First run: Emphasize setup command
- Errors present: Show validation/edit commands  
- Missing API keys: Show setup/edit for specific provider

### Examples in Help
Help text includes practical examples:
```bash
hlpr config setup --provider openai    # Setup for OpenAI
hlpr config show --key temperature     # Show single value
hlpr config reset --keep-api-keys      # Reset but keep credentials
```