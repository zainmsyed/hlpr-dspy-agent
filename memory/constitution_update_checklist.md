# hlpr Constitution Update Checklist

When amending the hlpr constitution (`/memory/constitution.md`), ensure all dependent documents are updated to maintain consistency with the project's core principles: modular architecture, privacy-first design, CLI-first experience, DSPy integration, and modern tooling.

## Templates to Update

### When adding/modifying ANY article:
- [ ] `/templates/plan-template.md` - Update Constitution Check section with hlpr principles
- [ ] `/templates/spec-template.md` - Update if DSPy/LLM requirements affected
- [ ] `/templates/tasks-template.md` - Update if modular development process changes
- [ ] `/templates/agent-file-template.md` - Update if new development patterns needed
- [ ] `/scripts/` - Update automation scripts if tooling requirements change
- [ ] `/README.md` - Update project overview if core principles affected

### Article-specific updates:

#### Article I (Modular Architecture):
- [ ] Ensure templates emphasize standalone module creation
- [ ] Update CLI command examples for modular structure
- [ ] Add module interface documentation requirements
- [ ] Update testing templates for independent module testing

#### Article II (Privacy-First Design):
- [ ] Update templates with local LLM default settings
- [ ] Add credential security reminders
- [ ] Include TLS/SSL requirements in network examples
- [ ] Add data flow transparency requirements

#### Article III (CLI-First Experience):
- [ ] Update CLI flag requirements in templates
- [ ] Add Rich/Typer integration examples
- [ ] Include interactive vs power mode considerations
- [ ] Update error handling patterns for user-friendly messages

#### Article IV (DSPy Integration & Optimization):
- [ ] Update AI workflow templates with DSPy requirements
- [ ] Add MIPRO optimization reminders
- [ ] Include provider flexibility examples (local vs cloud)
- [ ] Update timeout policy documentation

#### Article V (Modern Tooling & Quality):
- [ ] Update UV dependency management examples
- [ ] Add Ruff compliance requirements to templates
- [ ] Include type safety (Pydantic) patterns
- [ ] Update structured logging requirements

## Validation Steps

1. **Before committing constitution changes:**
   - [ ] All templates reference hlpr's modular architecture requirements
   - [ ] Examples updated to match privacy-first and CLI-first principles
   - [ ] DSPy integration patterns properly documented
   - [ ] UV/Ruff tooling requirements included
   - [ ] No contradictions with local LLM and security requirements

2. **After updating templates:**
   - [ ] Run through a sample hlpr feature implementation plan
   - [ ] Verify all constitution principles (modular, privacy, CLI, DSPy, tooling) addressed
   - [ ] Check that templates work with project venv: `/home/zain/Documents/coding/hlpr/.venv/bin/python`
   - [ ] Test UV dependency management examples: `uv add`, `uv run`

3. **hlpr-specific validation:**
   - [ ] Local LLM timeout policies properly documented (no timeout by default)
   - [ ] Keyring credential storage patterns included
   - [ ] TLS/SSL requirements for IMAP/email connections documented
   - [ ] DSPy/MIPRO optimization examples provided

## Version tracking:
- [ ] Update constitution version number
- [ ] Note version in template footers
- [ ] Add amendment to constitution history
- [ ] Update ratification date if major changes

## Common Misses in hlpr Updates

Watch for these often-forgotten hlpr-specific updates:
- DSPy workflow documentation (`/docs/local-dspy.md`)
- Email processing security requirements
- Local LLM endpoint configurations
- UV dependency management examples
- Privacy-first data handling patterns
- CLI interactive vs power mode examples

## Template Sync Status

Last sync check: 2025-09-18
- Constitution version: 1.0.0
- Templates aligned: ✅ (updated for hlpr modular architecture, privacy-first design, CLI-first experience, DSPy integration, modern tooling)

---

*This checklist ensures hlpr's constitution principles are consistently applied across all project documentation and maintains the project's focus on privacy, modularity, and AI-assisted workflows.*