"""Templates for configuration files and environment files.

Provides functions that return default YAML and .env file contents. These
are used by the CLI to initialize configuration files and by unit tests.
"""

from __future__ import annotations

from typing import Dict


def default_config_yaml(defaults: Dict[str, object]) -> str:
    """Return a YAML string for the default configuration.

    `defaults` should contain keys matching the UserConfiguration model.
    The function keeps YAML generation minimal and human-friendly.
    """
    lines: list[str] = []
    lines.append("# hlpr configuration file")
    for k, v in defaults.items():
        if isinstance(v, bool):
            val = "true" if v else "false"
        else:
            val = str(v)
        lines.append(f"{k}: {val}")
    return "\n".join(lines) + "\n"


def default_env_template() -> str:
    """Return a default .env template string with placeholders for API keys."""
    return (
        "# API keys for hlpr\n"
        "# Example: OPENAI_API_KEY=sk-...\n"
        "OPENAI_API_KEY=\n"
        "ANTHROPIC_API_KEY=\n"
        "GROQ_API_KEY=\n"
        "OPENROUTER_API_KEY=\n"
    )
