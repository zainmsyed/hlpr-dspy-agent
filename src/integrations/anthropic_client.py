from __future__ import annotations

import os
import time
from typing import Any


class AnthropicClient:
    """Minimal wrapper for Anthropic (Claude) style APIs.

    This is a conservative implementation that returns stubs when no API key
    is present and uses simple HTTP calls when provided.
    """

    def __init__(self, api_key: str | None = None, timeout: float = 10.0):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.timeout = timeout

    def predict(self, prompt: str, model: str = "claude-2.1", max_tokens: int | None = None, temperature: float = 0.0) -> dict[str, Any]:
        if not self.api_key:
            return {"model": model, "prompt": prompt, "result": self._stub(prompt)}

        try:
            import json
            from urllib import request as _request

            url = "https://api.anthropic.com/v1/complete"
            headers = {"Content-Type": "application/json", "x-api-key": self.api_key}
            body = {"model": model, "prompt": prompt, "max_tokens": max_tokens, "temperature": temperature}
            data = json.dumps(body).encode("utf-8")
            req = _request.Request(url, data=data, headers=headers, method="POST")
            with _request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
                j = json.loads(raw)
                text = j.get("completion") or j.get("completion_text") or j.get("text")
                return {"model": model, "prompt": prompt, "result": text or json.dumps(j)}
        except Exception:
            return {"model": model, "prompt": prompt, "result": self._stub(prompt)}

    def _stub(self, prompt: str) -> str:
        return f"[anthropic-stub at {time.strftime('%Y-%m-%d %H:%M:%S')}] {prompt[:400]}"

    def train(self, training_data: Any, **kwargs) -> dict[str, Any]:
        return {"ok": False, "reason": "anthropic-training-not-implemented"}
