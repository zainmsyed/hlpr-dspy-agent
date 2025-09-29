# Research: Interactive Save Prompt (Rich)

Decision: Use Rich's `rich.prompt.Confirm` and `rich.prompt.Prompt` for all interactive prompts in the CLI. Default answers: confirm save=Yes, format=md, output path=existing organized storage path.

Rationale: The project already uses Rich for terminal UI; reusing Rich prompts keeps a consistent user experience and allows testable monkeypatching in unit tests.

Alternatives considered:
- Use Typer's built-in prompts — rejected because Rich prompts provide better formatting and are already used elsewhere in the codebase.
- Use raw `input()` — rejected due to poor formatting and TTY handling differences.

Constitution check: Conforms to CLI-first and Modular Architecture principles. No security or privacy issues identified.

Open questions resolved:
- Overwrite behavior: append timestamp suffix to avoid overwriting (user choice recorded in spec Clarifications).
