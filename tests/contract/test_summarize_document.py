from pathlib import Path

from fastapi.testclient import TestClient

from src.hlpr.api.main import app

client = TestClient(app)

# HTTP status code constants
HTTP_200_OK = 200
HTTP_400_BAD_REQUEST = 400
HTTP_422_UNPROCESSABLE_ENTITY = 422


class TestSummarizeDocumentContract:
    """Contract tests for POST /summarize/document endpoint"""

    def test_summarize_document_with_file_upload(self):
        """Test document summarization with file upload (multipart/form-data)"""
        # This test will fail until the endpoint is implemented
        Path("test_document.txt").write_text(
            "This is a test document for summarization.",
        )

        with Path("test_document.txt").open("rb") as f:
            response = client.post(
                "/summarize/document",
                files={"file": ("test_document.txt", f, "text/plain")},
                data={"provider_id": "local", "save_format": "json"},
            )

        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "summary" in data
        assert "key_points" in data
        assert isinstance(data["key_points"], list)
        assert "word_count" in data
        assert "processing_time_ms" in data
        assert "provider_used" in data

    def test_summarize_document_with_text_content(self):
        """Test document summarization with raw text content (application/json)"""
        # This test will fail until the endpoint is implemented
        payload = {
            "text_content": (
                "This is a test document content for summarization purposes."
            ),
            "title": "Test Document",
            "provider_id": "local",
            "save_format": "json",
        }

        response = client.post("/summarize/document", json=payload)

        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "summary" in data
        assert "key_points" in data
        assert isinstance(data["key_points"], list)
        assert "word_count" in data
        assert "processing_time_ms" in data
        assert "provider_used" in data

    def test_summarize_document_invalid_request(self):
        """Test invalid request handling"""
        # Missing required fields
        response = client.post("/summarize/document", json={})

        assert response.status_code in [HTTP_400_BAD_REQUEST, HTTP_422_UNPROCESSABLE_ENTITY]
        data = response.json()
        assert "error" in data
        assert "error_code" in data

    def test_summarize_document_unsupported_format(self):
        """Test handling of unsupported file formats"""
        # This would test file validation, but since endpoint doesn't exist, it will fail
        # Placeholder for future implementation

    def test_summarize_document_file_too_large(self):
        """Test handling of files that are too large"""
        # This would test file size limits, but since endpoint doesn't exist, it will fail
        # Placeholder for future implementation
