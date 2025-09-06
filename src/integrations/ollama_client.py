from __future__ import annotations

import json
import os
import time
from typing import Any

try:
    # prefer standard library http client to avoid extra deps
    from urllib import request as _request
    from urllib.error import URLError, HTTPError
except Exception:  # pragma: no cover - extremely unlikely
    _request = None
    URLError = Exception
    HTTPError = Exception


class OllamaClient:
    """A small, safe wrapper around a local Ollama HTTP endpoint.

    Behavior:
    - Reads OLLAMA_BASE_URL and OLLAMA_MODEL from environment.
    - If the local service is unreachable, falls back to a stubbed response.
    - Does not require any third-party package at runtime.

    Note: This intentionally keeps the implementation conservative so it works
    in development even when Ollama isn't installed.
    """

    def __init__(self, base_url: str | None = None, model: str | None = None, timeout: float = 10.0):
        self.base_url = base_url or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.environ.get("OLLAMA_MODEL", "llama2")
        self.timeout = float(os.environ.get("OLLAMA_TIMEOUT", str(timeout)))

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = self.base_url.rstrip("/") + path
        data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        req = _request.Request(url, data=data, headers=headers, method="POST")
        try:
            with _request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
                try:
                    return json.loads(raw)
                except Exception:
                    return {"raw": raw}
        except (URLError, HTTPError, TimeoutError) as exc:  # pragma: no cover - network fallback
            raise ConnectionError(f"Ollama HTTP request failed: {exc}") from exc

    def list_models(self) -> list[str]:
        """Try to list available models from Ollama; on failure return empty list."""
        try:
            # Ollama exposes models at /api/models (best-effort)
            url = self.base_url.rstrip("/") + "/api/models"
            req = _request.Request(url, method="GET")
            with _request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw)
                # data may be list of model objects or names
                if isinstance(data, list):
                    names = [m.get("name") if isinstance(m, dict) else str(m) for m in data]
                    return [n for n in names if n]
        except Exception:
            return []
        return []

    def predict(self, prompt: str, model: str | None = None, max_tokens: int | None = None, temperature: float = 0.0) -> dict[str, Any]:
        """Generate text from the model.

        Returns a dict with at least keys: model, prompt, result.
        On connection failure, returns a safe stubbed response.
        """
        model = model or self.model
        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        # best-effort call to /api/generate (common Ollama HTTP endpoint)
        retries = int(os.environ.get("OLLAMA_RETRIES", "2"))
        backoff = float(os.environ.get("OLLAMA_BACKOFF", "0.5"))
        attempt = 0
        last_exc: Exception | None = None
        resp = None
        while attempt <= retries:
            try:
                resp = self._post_json("/api/generate", payload)
                last_exc = None
                break
            except ConnectionError as e:
                last_exc = e
                attempt += 1
                if attempt > retries:
                    break
                time.sleep(backoff * attempt)

        # If we got a response, try to normalize and return it
        if isinstance(resp, dict):
            # If we got a 'raw' key containing streaming JSON (ndjson), try to parse it
            raw = resp.get("raw")
            if isinstance(raw, str) and "\n{" in raw:
                parsed = self._parse_ndjson(raw)
                if parsed:
                    return {"model": model, "prompt": prompt, "result": parsed}

            if "result" in resp and isinstance(resp["result"], str):
                return {"model": model, "prompt": prompt, "result": resp["result"]}
            if "text" in resp and isinstance(resp["text"], str):
                return {"model": model, "prompt": prompt, "result": resp["text"]}
            # fallback: return JSON string
            return {"model": model, "prompt": prompt, "result": json.dumps(resp)}

        # If retries exhausted and no response, fall back to stubbed response
        if last_exc is not None and resp is None:
            pass

        stub = self._stub_response(prompt)
        return {"model": model, "prompt": prompt, "result": stub}

    def _stub_response(self, prompt: str) -> str:
        # simple deterministic stub that summarizes by truncation and timestamp
        snippet = prompt.strip().replace("\n", " ")[:400]
        return f"[ollama-stub summary at {time.strftime('%Y-%m-%d %H:%M:%S')}]: {snippet}"

    def _parse_ndjson(self, raw: str) -> str:
        """Parse newline-delimited JSON (ndjson) and extract text/response fields.

        Returns the concatenated text from known keys ('response','text','result') or
        an empty string if nothing useful found.
        """
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        parts: list[str] = []
        for line in lines:
            try:
                obj = json.loads(line)
            except Exception:
                # not JSON, skip
                continue
            # common fields to aggregate
            for key in ("response", "text", "result", "content"):
                if key in obj and isinstance(obj[key], str):
                    parts.append(obj[key])
                    break
            else:
                # fallback: if object has a single string value, take it
                for v in obj.values():
                    if isinstance(v, str):
                        parts.append(v)
                        break
        return "\n".join(parts).strip()

    def get_dspy_lm(self):
        """Return a DSPy language model instance for Ollama integration."""
        try:
            import dspy
            from dspy.clients.lm import LM
            class OllamaLM(LM):
                """A thin LM adapter that delegates generation to OllamaClient.

                Important: DSPy expects LM objects to expose a `model` attribute and
                to be callable (returning a list of text chunks). We ensure the
                adapter is initialized with the client's configured model name.
                """

                def __init__(self, ollama_client: "OllamaClient"):
                    # initialize the LM base with the model name from the client
                    model_name = getattr(ollama_client, "model", None) or "unknown"
                    super().__init__(model=model_name)
                    # also ensure attribute exists on the instance
                    self.model = model_name
                    self.ollama = ollama_client

                def __call__(self, prompt: str, **kwargs):
                    """Call OllamaClient.predict and return a list of text results.

                    We return a list of strings to match DSPy's expectation for
                    streaming/segmented outputs.
                    """
                    try:
                        resp = self.ollama.predict(prompt, **kwargs)
                        if isinstance(resp, dict):
                            return [resp.get("result", "")]
                        return [str(resp)]
                    except Exception as e:
                        # Return a safe single-item list on error so DSPy callers
                        # don't crash; include the error text for debugging.
                        return [f"[DSPy-Ollama Error]: {str(e)}"]

                def get_generate_kwargs(self, **kwargs):
                    """Normalize generation kwargs for DSPy callers."""
                    return {
                        "temperature": kwargs.get("temperature", 0.0),
                        "max_tokens": kwargs.get("max_tokens", 150),
                    }

            return OllamaLM(self)
        except ImportError:
            raise ImportError("DSPy is required for DSPy integration. Install with: pip install dspy-ai")

    def health_check(self) -> bool:
        """Quick health check against common endpoints. Returns True if service responds."""
        endpoints = ["/api/system", "/api/models", "/"]
        for ep in endpoints:
            url = self.base_url.rstrip("/") + ep
            try:
                req = _request.Request(url, method="GET")
                with _request.urlopen(req, timeout=self.timeout) as resp:
                    # Some servers return 200, others may return 204 etc.; treat 2xx as healthy
                    status = getattr(resp, "status", None)
                    if status is None:
                        # older urllib may not expose .status; assume success if read works
                        _ = resp.read()
                        return True
                    if 200 <= int(status) < 300:
                        return True
            except Exception:
                continue
        return False

