# Research: Update Config Workflow

**Date**: September 30, 2025  
**Status**: Complete  

## Research Questions & Findings

### Configuration File Formats
**Decision**: YAML for main config, .env for API keys  
**Rationale**: 
- YAML is human-readable and supports comments for user guidance
- .env format is familiar to developers and well-supported by libraries
- Separation allows different security treatments (YAML 644, .env 600)
- Both formats are easily editable with any text editor

**Alternatives Considered**:
- JSON: Less readable, no comments support
- TOML: Good but less familiar to users than YAML
- Single file: Security concerns mixing public preferences with API keys

### File Location Strategy
**Decision**: ~/.hlpr/ directory with config.yaml and .env files  
**Rationale**:
- Standard XDG-style location familiar to CLI users
- Allows future expansion (caches, logs, etc.)
- Platform-agnostic location (works on Linux, macOS, Windows)
- Easy to backup or version control (excluding .env)

**Alternatives Considered**:
- ~/.config/hlpr/: More XDG compliant but less discoverable
- ~/.hlpr.yaml: Single file approach, rejected for security reasons
- OS-specific locations: Complex, platform-dependent

### Configuration Loading Performance
**Decision**: In-memory caching with file modification checking  
**Rationale**:
- Target <100ms loading requires avoiding file I/O on every operation
- YAML parsing is relatively fast for small files (<1KB typical)
- File modification time checking is faster than re-parsing
- Memory footprint minimal for personal productivity tool

**Alternatives Considered**:
- Database storage: Overkill for simple key-value preferences
- Always reload: Too slow for <100ms requirement
- Write-through cache: Unnecessary complexity for single-user tool

### API Key Storage Security
**Decision**: .env file with chmod 600 permissions  
**Rationale**:
- Balances security with usability for personal tools
- Standard practice for CLI applications
- Easy to backup/restore configurations
- Compatible with existing .gitignore patterns

**Alternatives Considered**:
- System keyring: More secure but complex cross-platform implementation
- Encrypted files: Adds password management complexity
- Plain text with warnings: Insufficient security protection

### Configuration Migration Strategy
**Decision**: Detect existing config formats and migrate on first load  
**Rationale**:
- Seamless upgrade experience for existing users
- One-time operation, no ongoing performance impact
- Backup original files before migration
- Clear user notification of migration actions

**Alternatives Considered**:
- Manual migration: Poor user experience
- Parallel support: Code complexity and maintenance burden
- No migration: Breaking change for existing users

### Error Handling Approach
**Decision**: Graceful fallback with user choice (fail-soft pattern)  
**Rationale**:
- Keeps application functional even with config issues
- Provides clear user feedback and recovery options
- Aligns with privacy-first principle (works without cloud configs)
- Better user experience than hard failures

**Alternatives Considered**:
- Fail-fast: Poor user experience for config errors
- Silent fallback: Users unaware of configuration problems
- Interactive recovery only: Blocks automated usage

### Dependencies Required
**Decision**: Add PyYAML for YAML parsing  
**Rationale**:
- Standard library for YAML in Python ecosystem
- Lightweight dependency with no transitive dependencies
- Well-maintained and stable
- Good error reporting for malformed files

**Alternatives Considered**:
- ruamel.yaml: More features but heavier dependency
- Custom parser: Reinventing wheel, error-prone
- JSON only: Less user-friendly for manual editing

## Implementation Patterns

### Configuration Manager Pattern
- Single entry point for all config operations
- Lazy loading with caching
- Atomic file operations (write to temp, then rename)
- Clear separation of concerns (loading, validation, saving)

### Validation Strategy
- Pydantic models for type safety and validation
- Default value injection for missing fields
- Clear error messages with suggested fixes
- Progressive validation (basic -> advanced settings)

### CLI Integration Pattern
- Reuse existing Rich/Typer patterns from guided workflow
- Consistent command structure (setup, show, edit, reset)
- Interactive prompts with sensible defaults
- Non-interactive mode support for automation

## Risk Assessment

### Low Risk
- YAML parsing performance (small files)
- File permission handling (standard OS operations)
- Integration with existing CLI patterns

### Medium Risk
- Cross-platform file path handling (mitigated by pathlib)
- Configuration migration edge cases (mitigated by backups)
- User education for manual file editing (mitigated by examples/comments)

### High Risk
- None identified - straightforward file-based configuration system

## Success Metrics

### Performance Targets
- Configuration loading: <50ms average (well under 100ms requirement)
- Configuration saving: <50ms average (atomic operations)
- Memory footprint: <1MB for configuration subsystem

### User Experience Targets
- Zero configuration errors for default workflows
- <5 second guided setup completion
- Clear, actionable error messages for all failure modes
- Intuitive file format for manual editing

## Next Steps
All research questions resolved. Ready to proceed to Phase 1 design with:
1. Data model definition (Pydantic schemas)
2. API contract specification (ConfigurationManager interface)
3. Test scenario extraction from user stories
4. Quickstart validation procedures