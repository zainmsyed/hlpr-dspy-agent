
from hlpr.config.models import APICredentials, ProviderType


def test_get_key_for_provider_returns_none_by_default():
    creds = APICredentials()
    assert creds.get_key_for_provider(ProviderType.OPENAI) is None
    assert creds.get_key_for_provider(ProviderType.LOCAL) is None


def test_set_and_get_api_key():
    creds = APICredentials(openai_api_key="sk-test-123")
    assert creds.get_key_for_provider(ProviderType.OPENAI) == "sk-test-123"
