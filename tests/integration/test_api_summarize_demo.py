import io
import json
from fastapi.testclient import TestClient

from hlpr.api.main import app


def test_summarize_document_demo():
    client = TestClient(app)

    with open("test_document.txt", "rb") as f:
        files = {"file": ("test_document.txt", f, "text/plain")}
        resp = client.post("/summarize/document", files=files)

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "summary" in body
    assert "key_points" in body
    # Ensure either DSPy result or fallback present
    assert isinstance(body["summary"], str) and len(body["summary"]) > 0
