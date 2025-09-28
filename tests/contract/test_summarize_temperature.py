from fastapi.testclient import TestClient

from hlpr.api.main import app

client = TestClient(app)


def test_summarize_text_with_temperature_in_body():
    """POST raw text with an explicit temperature and expect a valid response."""
    payload = {
        "text_content": "This is a short sample text to test temperature forwarding.",
        "title": "Temp Test",
        "provider_id": "local",
        "temperature": 0.1,
        "format": "json",
    }

    response = client.post("/summarize/document", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "summary" in data
    assert isinstance(data.get("key_points", []), list)
    assert "processing_time_ms" in data


def test_summarize_text_temperature_query_param():
    """POST raw text with temperature provided as query param and
    expect a valid response.
    """
    payload = {
        "text_content": "Another tiny sample to test query param temperature.",
        "title": "Temp Query Test",
        "provider_id": "local",
        "format": "json",
    }

    response = client.post("/summarize/document?temperature=0.9", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "summary" in data
    assert isinstance(data.get("key_points", []), list)
    assert "processing_time_ms" in data
