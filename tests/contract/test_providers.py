from fastapi.testclient import TestClient

from hlpr.api.main import app

client = TestClient(app)


class TestProvidersContract:
    """Contract tests for GET /providers endpoint"""

    def test_get_providers_success(self):
        """Test successful retrieval of AI providers"""
        # This test will fail until the endpoint is implemented
        response = client.get("/providers")

        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert isinstance(data["providers"], list)

        # Should have at least one provider (local)
        assert len(data["providers"]) > 0

    def test_get_providers_structure(self):
        """Test that provider objects have required fields"""
        response = client.get("/providers")

        assert response.status_code == 200
        data = response.json()

        for provider in data["providers"]:
            required_fields = ["id", "type", "model_name", "is_default", "status"]
            for field in required_fields:
                assert field in provider

            # Type should be valid enum
            assert provider["type"] in ["LOCAL", "OPENAI", "ANTHROPIC"]

            # Status should be valid
            assert provider["status"] in ["AVAILABLE", "UNAVAILABLE", "ERROR"]

            # is_default should be boolean
            assert isinstance(provider["is_default"], bool)

    def test_get_providers_has_default(self):
        """Test that there is exactly one default provider"""
        response = client.get("/providers")

        assert response.status_code == 200
        data = response.json()

        default_providers = [p for p in data["providers"] if p["is_default"]]
        assert len(default_providers) == 1

    def test_get_providers_includes_local(self):
        """Test that local provider is always available"""
        response = client.get("/providers")

        assert response.status_code == 200
        data = response.json()

        local_providers = [p for p in data["providers"] if p["type"] == "LOCAL"]
        assert len(local_providers) >= 1

        # Local provider should be available
        for local in local_providers:
            assert local["status"] == "AVAILABLE"

    def test_get_providers_model_names(self):
        """Test that providers have valid model names"""
        response = client.get("/providers")

        assert response.status_code == 200
        data = response.json()

        for provider in data["providers"]:
            assert provider["model_name"]
            assert isinstance(provider["model_name"], str)
            assert len(provider["model_name"]) > 0
