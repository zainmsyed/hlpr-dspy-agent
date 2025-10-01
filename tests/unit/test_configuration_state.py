from hlpr.config import models


def test_configuration_state_has_api_key_check():
    state = models.ConfigurationState()
    # Local provider should not require API key
    assert state.has_api_key_for_provider(models.ProviderType.LOCAL)

    # Without keys, cloud providers return False
    assert not state.has_api_key_for_provider(models.ProviderType.OPENAI)
