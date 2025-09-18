from fastapi.testclient import TestClient


def test_correlation_header_included_when_enabled(monkeypatch):
    # Ensure header is enabled
    monkeypatch.setenv("HLPR_INCLUDE_CORRELATION_HEADER", "true")
    from importlib import reload

    import hlpr.config as cfg
    from hlpr.api import summarize
    from hlpr.api.main import app

    reload(cfg)
    # Patch the summarize module CONFIG used by endpoint
    summarize.CONFIG = cfg.HlprConfig.from_env()

    client = TestClient(app)

    resp = client.post(
        "/summarize/document",
        json={"text_content": "hello world", "title": "t"},
    )
    assert resp.status_code == 200
    assert "X-Correlation-ID" in resp.headers
    assert resp.headers["X-Correlation-ID"]


def test_correlation_header_absent_when_disabled(monkeypatch):
    monkeypatch.setenv("HLPR_INCLUDE_CORRELATION_HEADER", "false")
    from importlib import reload

    import hlpr.config as cfg
    from hlpr.api import summarize
    from hlpr.api.main import app

    reload(cfg)
    summarize.CONFIG = cfg.HlprConfig.from_env()

    client = TestClient(app)

    resp = client.post(
        "/summarize/document",
        json={"text_content": "hello world", "title": "t"},
    )
    assert resp.status_code == 200
    assert "X-Correlation-ID" not in resp.headers
