"""Centralized constants for guided mode configuration.

Place small, well-documented constants here so multiple modules can import
shared values instead of duplicating literals across the codebase.
"""

from __future__ import annotations

from collections.abc import Sequence

ALLOWED_PROVIDERS: Sequence[str] = (
    "local",
    "openai",
    "google",
    "anthropic",
    "openrouter",
    "groq",
    "deepseek",
    "glm",
    "cohere",
    "mistral",
)
ALLOWED_FORMATS: Sequence[str] = ("rich", "txt", "md", "json")

DEFAULT_PROVIDER = "local"
DEFAULT_FORMAT = "rich"
DEFAULT_CHUNK_SIZE = 8192
MAX_PROMPT_ATTEMPTS = 3

# Help text short summary; keep in sync with help_display DEFAULT_* dicts if used.
PROVIDER_SHORT_HELP = {
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

FORMAT_SHORT_HELP = {
    "rich": "Rich terminal output with panels and color (TTY required).",
    "txt": "Plain text output, good for piping to other tools.",
    "md": "Markdown-formatted output, suitable for saving as .md files.",
    "json": "Structured JSON output for programmatic consumption.",
}
