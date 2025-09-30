# Tasks: Interactive Save Prompt (Rich)

Feature: Interactive save prompt using Rich when `--save` is not provided. Privacy-first: no auto-save without explicit opt-in.
Branch: `006-title-interactive-save`

Execution order: TDD-first. Tests marked [P] may run in parallel when safe.

T001 - Setup: Ensure dev environment & dependencies [X]
- Path: N/A
- Action: Verify `rich` is available in the project environment. If not, add via `uv add rich` (project follows UV dependency management). Run `uv run pytest -q` to ensure baseline tests pass.
- Notes: This is a prerequisite task. Rich should already be available as it's used elsewhere in the project.

T002 [P] - Contract test: CLI behavior contract [X]
- Path: `tests/contract/test_cli_save_behavior.py`
- Action: Create contract-level test using Typer's testing utilities that validates CLI behavior without `--save` flag: (1) Interactive mode shows prompts, (2) Non-interactive mode with no opt-in saves nothing (privacy-first), (3) Non-interactive with `HLPR_AUTO_SAVE=true` saves with defaults. Test both document and meeting summarization commands.
- Output: Test file referencing `specs/006-title-interactive-save/contracts/cli-behavior.md`.

T003 [P] - Unit test: default interactive save (press Enter) [X]
- Path: `tests/unit/test_cli_save_prompt_default.py`
- Action: Monkeypatch `rich.prompt.Confirm.ask` and `rich.prompt.Prompt.ask` to simulate default responses (Confirm -> True, Format -> 'md', Path -> default organized storage path). Import and call the summarize function directly with mocked prompts. Assert file created at expected organized storage path with correct markdown content format.

T004 [P] - Unit test: user declines save [X]
- Path: `tests/unit/test_cli_save_prompt_decline.py`
- Action: Monkeypatch `rich.prompt.Confirm.ask` to return False. Run summarize function and assert no file was created and appropriate message shown.

T005 [P] - Unit test: format selection and JSON content [X]
- Path: `tests/unit/test_cli_save_prompt_json.py`
- Action: Monkeypatch Rich prompts: Confirm -> True, Format -> 'json', Path -> test output path. Assert JSON file exists with required fields (`summary`, `generated_at` as valid ISO8601) and atomic write was used.

T006 [P] - Unit test: non-interactive privacy-first behavior [X]
- Path: `tests/unit/test_cli_save_prompt_non_tty.py`
- Action: Mock `sys.stdin.isatty()` to return False. Test privacy-first behavior: (1) Default non-interactive run saves nothing, (2) With `HLPR_AUTO_SAVE=true` env var saves with defaults (md format, organized storage path). Validate environment variable parsing and privacy compliance.

T007 [P] - Unit test: existing-file collision handling [X]
- Path: `tests/unit/test_cli_save_prompt_collision.py`
- Action: Create existing file at target path. Run save flow and assert new file created with timestamp suffix `_YYYYMMDDTHHMMSS`, original file unchanged. Test timestamp format is valid and parseable.

T008 [P] - Unit test: StorageError handling [X]
- Path: `tests/unit/test_cli_save_error_handling.py`
- Action: Mock various write failures (permission denied, disk full, etc.). Assert that low-level errors are caught and surfaced as `StorageError` with helpful details. Verify user-friendly error messages are displayed in CLI.

T009 - Implementation: Timestamp suffix helper [X]
- Path: `src/hlpr/cli/summarize.py`
- Action: Implement `_unique_path_with_timestamp(path: Path) -> Path` that appends `_YYYYMMDDTHHMMSS` before file extension if path exists. Use `datetime.now().strftime('%Y%m%dT%H%M%S')` for timestamp format. Keep helper local to CLI module since it's file naming strategy.

T010 - Implementation: Add Rich prompts to CLI [X]
- Path: `src/hlpr/cli/summarize.py`
- Action: Add `_interactive_save_flow(document, result, output_format, output, prefs)` helper that:
  - Imports `from rich.prompt import Confirm, Prompt`
  - Checks `sys.stdin.isatty()` for interactivity and `os.environ.get('HLPR_AUTO_SAVE')` for opt-in
  - Interactive: Rich prompts for confirm (default True), format (choices=['md','txt','json'], default='md'), path (default from organized storage)
  - Non-interactive: privacy-first (no save) unless HLPR_AUTO_SAVE=true
  - Uses `_unique_path_with_timestamp()` for collision avoidance
  - Calls `atomic_write_text()` for safe persistence, handles JSON format with `generated_at`
  - Integrate into `summarize_document` and `summarize_meeting` after `_display_summary()`

T011 - Docs: Update quickstart and CLI documentation [X]
- Path: `specs/006-title-interactive-save/quickstart.md` and `docs/save-summaries.md`
- Action: Update quickstart to reflect privacy-first behavior (no auto-save without opt-in). Document environment variable `HLPR_AUTO_SAVE=true` for CI/automation. Add examples of interactive prompts and timestamp collision handling.

T012 - Polish: Lint, types, and run tests
- Path: repo root
- Action: Run `uvx ruff format && uvx ruff check` to ensure code quality. Run `uv run pytest tests/unit/test_cli_save_* tests/contract/test_cli_save_*` to validate all new tests pass. Fix any lint/type/test failures.

## Parallel Execution Groups

**Group A [P] - Test Creation**: T002, T003, T004, T005, T006, T007, T008 (all test files, can be written in parallel)

**Group B - Implementation**: T009 → T010 (helper first, then main implementation)

**Group C - Finalization**: T011, T012 (docs and polish)

## Dependencies & Execution Order

1. **Setup**: T001 (verify environment)
2. **Test Phase**: T002-T008 [P] (create all test files in parallel)
3. **Implementation Phase**: T009 → T010 (timestamp helper → main CLI integration)
4. **Documentation**: T011 (update docs with actual behavior)
5. **Quality Assurance**: T012 (lint, format, run tests)

## Testing Strategy Notes

- **Test Invocation**: Use direct function imports with monkeypatched Rich prompts for unit tests; use Typer testing for contract tests
- **Privacy Validation**: Ensure tests verify that non-interactive runs are privacy-first (no unexpected saves)
- **Environment Handling**: Test HLPR_AUTO_SAVE environment variable parsing and behavior
- **Error Scenarios**: Comprehensive error handling tests for StorageError mapping

Estimated total tasks: 12
