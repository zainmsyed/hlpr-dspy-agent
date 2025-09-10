from fastapi.testclient import TestClient

from hlpr.api.main import app

client = TestClient(app)


class TestEmailProcessContract:
    """Contract tests for POST /email/process endpoint"""

    def test_email_process_basic(self):
        """Test basic email processing request"""
        # This test will fail until the endpoint is implemented
        payload = {
            "account_id": "test_account",
            "mailbox": "INBOX",
            "filters": {
                "unread_only": True,
                "limit": 10,
            },
            "provider_id": "local",
        }

        response = client.post("/email/process", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert "account_id" in data
        assert data["account_id"] == "test_account"
        assert "emails_found" in data
        assert isinstance(data["emails_found"], int)
        assert "status" in data
        assert data["status"] in ["STARTED", "COMPLETED"]

    def test_email_process_with_filters(self):
        """Test email processing with various filters"""
        payload = {
            "account_id": "test_account",
            "filters": {
                "unread_only": False,
                "since_date": "2025-09-01",
                "from_sender": "test@example.com",
                "limit": 50,
            },
        }

        response = client.post("/email/process", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert "emails_found" in data

    def test_email_process_invalid_account(self):
        """Test processing with invalid account ID"""
        payload = {
            "account_id": "nonexistent_account",
        }

        response = client.post("/email/process", json=payload)

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "error_code" in data

    def test_email_process_missing_account_id(self):
        """Test request without required account_id"""
        response = client.post("/email/process", json={})

        assert response.status_code in [400, 422]
        data = response.json()
        assert "error" in data

    def test_email_process_authentication_failure(self):
        """Test handling of authentication failures"""
        # This would test IMAP auth failures, but since endpoint doesn't exist, it will fail
        # Placeholder for future implementation

    def test_email_process_large_limit(self):
        """Test processing with large email limit"""
        payload = {
            "account_id": "test_account",
            "filters": {
                "limit": 1000,  # Max allowed
            },
        }

        response = client.post("/email/process", json=payload)

        # Should either succeed or return error for limit exceeded
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = response.json()
            assert "job_id" in data
