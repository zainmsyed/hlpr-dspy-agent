from fastapi.testclient import TestClient

from hlpr.api.main import app

client = TestClient(app)


class TestSummarizeMeetingContract:
    """Contract tests for POST /summarize/meeting endpoint"""

    def test_summarize_meeting_with_content(self):
        """Test meeting summarization with raw text content"""
        # This test will fail until the endpoint is implemented
        payload = {
            "content": (
                "Meeting notes: Discussed project timeline. Action items: "
                "John to update docs by Friday."
            ),
            "title": "Project Planning Meeting",
            "date": "2025-09-09T10:00:00Z",
            "provider_id": "local",
        }

        response = client.post("/summarize/meeting", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "overview" in data
        assert "key_points" in data
        assert isinstance(data["key_points"], list)
        assert "action_items" in data
        assert isinstance(data["action_items"], list)
        assert "participants" in data
        assert isinstance(data["participants"], list)
        assert "processing_time_ms" in data

    def test_summarize_meeting_invalid_request(self):
        """Test invalid request handling"""
        # Missing required content
        response = client.post("/summarize/meeting", json={"title": "Test"})

        assert response.status_code in [400, 422]
        data = response.json()
        assert "error" in data
        assert "error_code" in data

    def test_summarize_meeting_empty_content(self):
        """Test handling of empty content"""
        payload = {
            "content": "",
            "title": "Empty Meeting",
        }

        response = client.post("/summarize/meeting", json=payload)

        # Should still process but with minimal results
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "overview" in data

    def test_summarize_meeting_with_action_items(self):
        """Test extraction of action items from meeting content"""
        payload = {
            "content": (
                "John will update the documentation. Sarah needs to review the code. "
                "Team to discuss budget next week."
            ),
            "title": "Development Meeting",
        }

        response = client.post("/summarize/meeting", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "action_items" in data
        assert isinstance(data["action_items"], list)
        # Should extract at least some action items
        assert len(data["action_items"]) > 0

    def test_summarize_meeting_processing_error(self):
        """Test handling of processing errors"""
        # This would test LLM failures, but since endpoint doesn't exist, it will fail
        # Placeholder for future implementation
