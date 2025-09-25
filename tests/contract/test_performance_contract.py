import pytest

try:
    from hlpr.config.loader import ConfigLoader
except Exception:  # noqa: BLE001
    ConfigLoader = None

import time


def test_configuration_startup_performance_contract():
    if ConfigLoader is None:
        pytest.fail("ConfigLoader not implemented yet")
    loader = ConfigLoader(None, None)
    start = time.time()
    result = loader.load_config()
    elapsed_ms = (time.time() - start) * 1000
    assert hasattr(result, "load_time_ms")
    assert result.load_time_ms < 100 or elapsed_ms < 100
