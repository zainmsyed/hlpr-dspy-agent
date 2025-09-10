from fastapi.testclient import TestClient

from src.hlpr.api.main import app

client = TestClient(app)


class TestEmailAccountsPostContract:
    """Contract tests for POST /email/accounts endpoint"""

    def test_create_email_account_success(self):
        """Test successful email account creation"""
        # This test will fail until the endpoint is implemented
        payload = {
            "id": "test_gmail",
            "provider": "GMAIL",
            "host": "imap.gmail.com",
            "port": 993,
            "username": "test@gmail.com",
            "password": "test_password",
            "default_mailbox": "INBOX",
            "use_tls": True,
        }

        response = client.post("/email/accounts", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["id"] == "test_gmail"
        assert "provider" in data
        assert data["provider"] == "GMAIL"
        assert "username" in data
        assert data["username"] == "test@gmail.com"
        assert "host" in data
        assert data["host"] == "imap.gmail.com"

    def test_create_email_account_custom_provider(self):
        """Test creating account with custom provider"""
        payload = {
            "id": "test_custom",
            "provider": "CUSTOM",
            "host": "mail.example.com",
            "username": "user@example.com",
            "password": "password123",
        }

        response = client.post("/email/accounts", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "test_custom"
        assert data["provider"] == "CUSTOM"

    def test_create_email_account_invalid_config(self):
        """Test creation with invalid configuration"""
        # Missing required fields
        payload = {
            "id": "invalid_account",
            "provider": "GMAIL",
            # Missing username, password, host
        }

        response = client.post("/email/accounts", json=payload)

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "error_code" in data

    def test_create_email_account_duplicate_id(self):
        """Test creating account with duplicate ID"""
        # First create an account
        payload = {
            "id": "duplicate_test",
            "provider": "GMAIL",
            "host": "imap.gmail.com",
            "username": "test@gmail.com",
            "password": "password",
        }

        # Create first account
        response1 = client.post("/email/accounts", json=payload)
        if response1.status_code == 201:
            # Try to create again with same ID
            response2 = client.post("/email/accounts", json=payload)
            assert response2.status_code == 409
            data = response2.json()
            assert "error" in data

    def test_create_email_account_invalid_provider(self):
        """Test creation with invalid provider"""
        payload = {
            "id": "invalid_provider",
            "provider": "INVALID",
            "host": "mail.example.com",
            "username": "user@example.com",
            "password": "password",
        }

        response = client.post("/email/accounts", json=payload)

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    def test_create_email_account_invalid_id_format(self):
        """Test creation with invalid ID format"""
        payload = {
            "id": "invalid id with spaces",
            "provider": "GMAIL",
            "host": "imap.gmail.com",
            "username": "test@gmail.com",
            "password": "password",
        }

        response = client.post("/email/accounts", json=payload)

        # Should fail due to ID pattern validation
        assert response.status_code in [400, 422]
