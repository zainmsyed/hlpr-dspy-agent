
from src.integrations.ollama_client import OllamaClient


def test_parse_ndjson_simple():
    raw = '{"response":"Hello"}\n{"response":" world"}\n'
    c = OllamaClient()
    parsed = c._parse_ndjson(raw)
    assert parsed.replace('\n', '') == 'Hello world'


def test_predict_parses_ndjson(monkeypatch):
    raw = '{"response":"Hi"}\n{"response":" there"}\n'

    def fake_post(path, payload):
        return {"raw": raw}

    c = OllamaClient()
    monkeypatch.setattr(c, "_post_json", fake_post)
    out = c.predict("hi", model="gemma3:latest")
    assert "result" in out
    assert "Hi" in out["result"]


def test_health_check_mock(monkeypatch):
    c = OllamaClient()

    def fake_urlopen(req, timeout=None):
        class R:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                pass

            def read(self):
                return b"{}"

        return R()

    # Monkeypatch urllib.request.urlopen used inside health_check
    import src.integrations.ollama_client as mod

    monkeypatch.setattr(mod._request, "urlopen", fake_urlopen)
    assert c.health_check() is True


def test_predict_malformed_ndjson(monkeypatch):
    # raw contains malformed JSON lines; parser should skip non-json and return joined parts
    raw = '{"response":"OK"}\nnotjson\n{"response":"done"}\n'

    def fake_post(path, payload):
        return {"raw": raw}

    c = OllamaClient()
    monkeypatch.setattr(c, "_post_json", fake_post)
    out = c.predict("hello", model="gemma3:latest")
    assert "OK" in out["result"] and "done" in out["result"]


def test_predict_retries_on_failure(monkeypatch):
    calls = {"count": 0}

    def fake_post(path, payload):
        calls["count"] += 1
        if calls["count"] < 3:
            raise ConnectionError("timeout")
        return {"result": "ok"}

    c = OllamaClient()
    monkeypatch.setenv("OLLAMA_RETRIES", "3")
    monkeypatch.setenv("OLLAMA_BACKOFF", "0")
    monkeypatch.setattr(c, "_post_json", fake_post)
    out = c.predict("hi", model="gemma3:latest")
    assert out["result"] == "ok"
    assert calls["count"] == 3
