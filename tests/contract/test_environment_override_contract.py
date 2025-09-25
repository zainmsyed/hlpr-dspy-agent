import os

import pytest

try:
    from hlpr.config.loader import ConfigLoader
except Exception:  # noqa: BLE001
    ConfigLoader = None


def test_environment_override_precedence():
    if ConfigLoader is None:
        pytest.fail("ConfigLoader not implemented yet")
    os.environ["HLPR_DEFAULT_PROVIDER"] = "openai"
    loader = ConfigLoader(None, None)
    result = loader.load_config()
    assert hasattr(result, "config")
    # Cleanup
    del os.environ["HLPR_DEFAULT_PROVIDER"]
