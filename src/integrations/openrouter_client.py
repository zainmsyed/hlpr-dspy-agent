from __future__ import annotations

import os
import time
from typing import Any


class OpenRouterClient:
    """Minimal wrapper for OpenRouter which proxies to different providers.

    Uses OPENROUTER_API_KEY environment variable if available. Falls back to stub.
    """

    def __init__(self, api_key: str | None = None, timeout: float = 10.0):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        self.timeout = timeout

    def predict(self, prompt: str, model: str = "gpt-4o-mini", **kwargs) -> dict[str, Any]:
        if not self.api_key:
            return {"model": model, "prompt": prompt, "result": self._stub(prompt)}

        try:
            import json
            from urllib import request as _request

            url = "https://api.openrouter.ai/v1/chat/completions"
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
            body = {"model": model, "messages": [{"role": "user", "content": prompt}]}
            data = json.dumps(body).encode("utf-8")
            req = _request.Request(url, data=data, headers=headers, method="POST")
            with _request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
                j = json.loads(raw)
                choice = j.get("choices", [{}])[0]
                text = choice.get("message", {}).get("content") or choice.get("text")
                return {"model": model, "prompt": prompt, "result": text or json.dumps(j)}
        except Exception:
            return {"model": model, "prompt": prompt, "result": self._stub(prompt)}

    def _stub(self, prompt: str) -> str:
        return f"[openrouter-stub at {time.strftime('%Y-%m-%d %H:%M:%S')}] {prompt[:400]}"

    def train(self, training_data: Any, **kwargs) -> dict[str, Any]:
        return {"ok": False, "reason": "openrouter-training-not-implemented"}
