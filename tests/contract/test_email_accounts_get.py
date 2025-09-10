from fastapi.testclient import TestClient

from hlpr.api.main import app

client = TestClient(app)


class TestEmailAccountsGetContract:
    """Contract tests for GET /email/accounts endpoint"""

    def test_get_email_accounts_success(self):
        """Test successful retrieval of email accounts"""
        # This test will fail until the endpoint is implemented
        response = client.get("/email/accounts")

        assert response.status_code == 200
        data = response.json()
        assert "accounts" in data
        assert isinstance(data["accounts"], list)

        # If there are accounts, check structure
        if data["accounts"]:
            account = data["accounts"][0]
            assert "id" in account
            assert "provider" in account
            assert account["provider"] in ["GMAIL", "OUTLOOK", "CUSTOM"]
            assert "username" in account
            assert "host" in account
            # last_sync may be null
            assert "last_sync" in account

    def test_get_email_accounts_empty(self):
        """Test retrieval when no accounts are configured"""
        # This test will fail until the endpoint is implemented
        response = client.get("/email/accounts")

        assert response.status_code == 200
        data = response.json()
        assert "accounts" in data
        assert isinstance(data["accounts"], list)
        # Could be empty or have accounts depending on setup

    def test_get_email_accounts_structure(self):
        """Test that account objects have required fields"""
        response = client.get("/email/accounts")

        assert response.status_code == 200
        data = response.json()

        for account in data["accounts"]:
            required_fields = ["id", "provider", "username", "host"]
            for field in required_fields:
                assert field in account
                assert account[field] is not None

            # Provider should be valid enum
            assert account["provider"] in ["GMAIL", "OUTLOOK", "CUSTOM"]

    def test_get_email_accounts_no_credentials(self):
        """Test that credentials are not included in response"""
        response = client.get("/email/accounts")

        assert response.status_code == 200
        data = response.json()

        for account in data["accounts"]:
            # Should not contain password or other sensitive fields
            assert "password" not in account
            assert "auth_token" not in account
