from __future__ import annotations

from typing import Any
from config.settings import get_settings

from .ollama_client import OllamaClient


class ProviderManager:
    """Selects and exposes a unified interface to multiple LLM providers.

    Usage:
        mgr = ProviderManager()
        resp = mgr.predict("hello world")
    """

    def __init__(self, provider: str | None = None):
        settings = get_settings()
        self.provider = provider or settings.provider_name or "ollama"
        self.settings = settings
        # instantiate provider-specific clients lazily
        self._clients: dict[str, Any] = {}

    def _get_client(self, name: str):
        if name == "ollama":
            if "ollama" not in self._clients:
                self._clients["ollama"] = OllamaClient(base_url=None, model=None, timeout=self.settings.provider_timeout)
            return self._clients["ollama"]
        # other clients are implemented in their own modules
        if name == "openai":
            from .openai_client import OpenAIClient

            if "openai" not in self._clients:
                self._clients["openai"] = OpenAIClient(api_key=self.settings.openai_api_key, timeout=self.settings.provider_timeout)
            return self._clients["openai"]
        if name == "anthropic":
            from .anthropic_client import AnthropicClient

            if "anthropic" not in self._clients:
                self._clients["anthropic"] = AnthropicClient(api_key=self.settings.anthropic_api_key, timeout=self.settings.provider_timeout)
            return self._clients["anthropic"]
        if name == "openrouter":
            from .openrouter_client import OpenRouterClient

            if "openrouter" not in self._clients:
                self._clients["openrouter"] = OpenRouterClient(api_key=self.settings.openrouter_api_key, timeout=self.settings.provider_timeout)
            return self._clients["openrouter"]
        if name == "google":
            from .google_client import GoogleClient

            if "google" not in self._clients:
                self._clients["google"] = GoogleClient(api_key=self.settings.google_api_key, timeout=self.settings.provider_timeout)
            return self._clients["google"]

        raise ValueError(f"Unknown provider: {name}")

    def predict(self, prompt: str, **kwargs) -> dict[str, Any]:
        client = self._get_client(self.provider)
        if hasattr(client, "predict"):
            return client.predict(prompt, **kwargs)
        raise NotImplementedError("Selected provider does not implement predict")

    def train(self, training_data: Any, **kwargs) -> dict[str, Any]:
        """Optional training API. Providers may implement a training method or return not-supported."""
        client = self._get_client(self.provider)
        if hasattr(client, "train"):
            return client.train(training_data, **kwargs)
        return {"ok": False, "reason": "training-not-supported"}
