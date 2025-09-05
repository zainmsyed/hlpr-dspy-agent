# Providers configuration

This project supports multiple LLM providers. Configure the provider and API keys via environment variables or the `config.Settings` class.

Common environment variables:

- `PROVIDER_NAME` or `provider_name` in settings: one of `ollama`, `openai`, `anthropic`, `google`, `openrouter`.
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `GOOGLE_API_KEY` - Google Cloud API key (or configure application default credentials for Vertex AI)
- `OPENROUTER_API_KEY` - OpenRouter API key

Example usage in code:

```python
from src.integrations.provider_manager import ProviderManager

mgr = ProviderManager()  # picks provider from config
resp = mgr.predict("Summarize this email: ...")
```

Notes on training:

- Training/fine-tuning flows are provider-specific and may require additional setup or SDKs.
- The included clients expose a `train(training_data)` method but most are stubs that return `training-not-implemented`.
