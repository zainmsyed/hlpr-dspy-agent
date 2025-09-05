from typing import Any

class OllamaClient:
    """Minimal stub for Ollama model client."""
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or "http://localhost:11434"

    def predict(self, prompt: str, **kwargs) -> dict[str, Any]:
        # placeholder implementation
        return {"model": "ollama-stub", "prompt": prompt, "result": "stubbed response"}
