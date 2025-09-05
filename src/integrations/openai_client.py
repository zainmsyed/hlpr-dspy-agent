from __future__ import annotations

import os
import time
from typing import Any


class OpenAIClient:
    """Minimal wrapper for OpenAI HTTP API.

    This implementation is intentionally minimal and uses the REST API via urllib
    so it doesn't require the official openai package. It supports predict (chat/completions)
    and a training stub (not implemented).
    """

    def __init__(self, api_key: str | None = None, timeout: float = 10.0):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.timeout = timeout

    def predict(self, prompt: str, model: str = "gpt-4o-mini", max_tokens: int | None = None, temperature: float = 0.0) -> dict[str, Any]:
        # For safety, if no API key, return a stubbed response
        if not self.api_key:
            return {"model": model, "prompt": prompt, "result": self._stub(prompt)}

        # Lightweight POST to OpenAI API using standard library to avoid extra deps
        try:
            import json
            from urllib import request as _request

            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
            body = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            data = json.dumps(body).encode("utf-8")
            req = _request.Request(url, data=data, headers=headers, method="POST")
            with _request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
                j = json.loads(raw)
                # simple normalization
                choice = j.get("choices", [{}])[0]
                text = choice.get("message", {}).get("content") or choice.get("text")
                return {"model": model, "prompt": prompt, "result": text or json.dumps(j)}
        except Exception:
            return {"model": model, "prompt": prompt, "result": self._stub(prompt)}

    def _stub(self, prompt: str) -> str:
        return f"[openai-stub at {time.strftime('%Y-%m-%d %H:%M:%S')}] {prompt[:400]}"

    def train(self, training_data: Any, **kwargs) -> dict[str, Any]:
        # OpenAI fine-tuning requires external flows; expose a consistent interface but mark unsupported here
        return {"ok": False, "reason": "openai-training-not-implemented"}
