from pathlib import Path

from fastapi.testclient import TestClient

from hlpr.api.main import app


def test_summarize_document_demo():
    client = TestClient(app)

    with Path("test_document.txt").open("rb") as f:
        files = {"file": ("test_document.txt", f, "text/plain")}
        resp = client.post("/summarize/document", files=files)

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "summary" in body
    assert "key_points" in body
    # Ensure either DSPy result or fallback present
    assert isinstance(body["summary"], str)
    assert len(body["summary"]) > 0
