import json
import time

from hlpr.config.loader import ConfigLoader
from hlpr.config.validators import ConfigValidator


def test_config_load_and_validate_performance(tmp_path):
    # Create a moderately-sized config file to simulate real load
    p = tmp_path / "config.json"
    cfg = {"defaults": {"default_provider": "local", "output_format": "rich", "chunk_size": 8192}}
    p.write_text(json.dumps(cfg))

    loader = ConfigLoader(config_path=p)

    start = time.perf_counter()
    result = loader.load_config()
    load_ms = (time.perf_counter() - start) * 1000.0

    validator = ConfigValidator()
    start2 = time.perf_counter()
    vr = validator.validate_config(result.config.as_dict())
    validate_ms = (time.perf_counter() - start2) * 1000.0

    # Assert basic correctness
    assert vr.is_valid

    # Performance targets: relaxed in CI; assert non-pathological behavior
    # We expect load to be reasonably fast (100ms) and validation very quick (10ms)
    # Allow generous headroom on CI machines.
    assert load_ms < 500, f"config load too slow: {load_ms:.1f}ms"
    assert validate_ms < 200, f"validation too slow: {validate_ms:.1f}ms"
