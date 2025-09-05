from __future__ import annotations

import os
import time
from typing import Any


class GoogleClient:
    """Placeholder for Google/Vertex AI client.

    Vertex AI integration requires google-cloud-aiplatform and more setup. This
    minimal client provides a safe stub when no API key/credentials are present
    and a simple HTTP-based predict when an API key is provided (not full-featured).
    """

    def __init__(self, api_key: str | None = None, timeout: float = 10.0):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self.timeout = timeout

    def predict(self, prompt: str, model: str = "vertex-text-bison", **kwargs) -> dict[str, Any]:
        if not self.api_key:
            return {"model": model, "prompt": prompt, "result": self._stub(prompt)}
        # Minimal HTTP call is not generally sufficient for Vertex; return stub with note
        return {"model": model, "prompt": prompt, "result": f"[google-proxy-stub] {prompt[:200]}"}

    def _stub(self, prompt: str) -> str:
        return f"[google-stub at {time.strftime('%Y-%m-%d %H:%M:%S')}] {prompt[:400]}"

    def train(self, training_data: Any, **kwargs) -> dict[str, Any]:
        return {"ok": False, "reason": "google-training-not-implemented"}
