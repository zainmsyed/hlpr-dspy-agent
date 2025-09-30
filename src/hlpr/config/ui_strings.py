"""User-facing strings and short help text for the hlpr guided workflow.

Centralize UI messages and help summaries so they can be reused across
validators, prompts, and help display components, and so they are easier to
translate or test.
"""

from __future__ import annotations

from collections.abc import Mapping

# Validation / file messages
EMPTY_PATH_MSG = "Empty path: provide a valid file path (e.g. /home/user/doc.md)"
FILE_NOT_FOUND_NO_EXT = (
    "File not found: '{path}'. Try adding a file extension (e.g. '{path}.md')"
    " or use an absolute path"
)

FILE_NOT_FOUND = "File not found: '{path}'. Verify the path and try again"

NOT_A_FILE = (
    "Path exists but is not a file: '{path}'. Provide a file path, not a directory"
)

FILE_NOT_READABLE = (
    "File is not readable: '{path}'. Check file permissions (chmod)"
    " or run with appropriate user"
)

ACCESS_COULD_NOT_BE_DETERMINED = (
    "File accessibility could not be determined for '{path}'."
    " Check path and permissions"
)

# Config validation messages
OPTIONS_MUST_BE_DICT = "Options must be a mapping/dict (e.g., {'provider': 'local'})"
MISSING_REQUIRED_TEMPLATE = (
    "Missing required option: '{key}'. Provide --{arg} or use guided mode prompts"
)

UNSUPPORTED_PROVIDER_TEMPLATE = (
    "Unsupported provider: '{provider}'. Supported providers: {allowed}"
)

UNSUPPORTED_FORMAT_TEMPLATE = (
    "Unsupported output format: '{ofmt}'. Supported formats: {allowed}"
)

# Prompt validation messages
PROVIDER_EMPTY_MSG = "Provider must be a non-empty string"
PROVIDER_UNSUPPORTED_TEMPLATE = (
    "Unsupported provider: '{provider}'. Supported: {allowed}"
)

FORMAT_EMPTY_MSG = "Format must be a non-empty string"
FORMAT_UNSUPPORTED_TEMPLATE = "Unsupported format: '{fmt}'. Supported: {allowed}"
TEMPERATURE_INVALID_MSG = "Temperature must be a number between 0.0 and 1.0"
TEMPERATURE_RANGE_MSG = "Temperature must be between 0.0 and 1.0"

# Quick help text used by HelpDisplay
PROVIDER_HELP: Mapping[str, str] = {
    "local": "Fast offline processing. Good for small docs and privacy-sensitive data.",
    "openai": "OpenAI GPT models - high quality, requires API key and credits.",
    "google": "Google Gemini models - competitive quality, requires API key.",
    "anthropic": "Anthropic Claude models - excellent for analysis, requires API key.",
    "openrouter": "Access multiple models through OpenRouter, requires API key.",
    "groq": "Fast inference with Groq hardware acceleration, requires API key.",
    "deepseek": "DeepSeek models - good for coding tasks, requires API key.",
    "glm": "ChatGLM models - multilingual support, requires API key.",
    "cohere": "Cohere models - good for embeddings and text tasks, requires API key.",
    "mistral": "Mistral models - European AI provider, requires API key.",
}

FORMAT_HELP: Mapping[str, str] = {
    "rich": "Rich terminal output with panels and color (TTY required).",
    "txt": "Plain text output, good for piping to other tools.",
    "md": "Markdown-formatted output, suitable for saving as .md files.",
    "json": "Structured JSON output for programmatic consumption.",
}

QUICK_HELP = (
    "Use guided mode to interactively select provider, format, and advanced options.\n"
    "Press Enter to accept defaults. Use --execute to run real processing."
)

# Success messages
SUCCESS_GUIDED = "Guided mode completed successfully"

# Common panel titles and messages
PANEL_STARTING = "Starting"
PANEL_COMPLETE = "Complete"
PANEL_INTERRUPTED = "Interrupted"
PANEL_COMMAND_TEMPLATE = "Command Template"

PROCESSING_FINISHED = "Processing finished successfully"
PROCESSING_INTERRUPTED = (
    "Processing was interrupted by user. Partial results preserved."
)
USER_CANCELLED = "User cancelled the guided workflow"

# Help panel titles
PANEL_PROVIDER_HELP = "AI Providers"
PANEL_FORMAT_HELP = "Output Formats"
NO_HELP_AVAILABLE = "No help available for '{name}'"

# Additional common panel titles used across interactive flows
PANEL_VALIDATION_ERROR = "Validation Error"
PANEL_PROCESSING_ERROR = "Processing Error"
PANEL_GUIDED_WORKFLOW_ERROR = "Guided Workflow Error"

# Phase and progress labels (used by PhaseTracker / ProgressTracker)
PHASE_VALIDATION = "Validation"
PHASE_PROCESSING = "Processing"
PHASE_RENDERING = "Rendering"

# Default description used by ProgressTracker when none provided
PROGRESS_WORKING = "Working"

# Suggestion strings used by validators.suggest_file_fixes
SUGGEST_EMPTY_PATH = "Provide a non-empty file path (absolute path recommended)"

# Simple messages used by non-UI modules
UNSUPPORTED_PROVIDER_SIMPLE = "Unsupported provider: {provider}"
UNSUPPORTED_FORMAT_SIMPLE = "Unsupported format: {fmt}"
