import pytest

try:
    from hlpr.config.ui_strings import UIStringManager
except Exception:  # noqa: BLE001
    UIStringManager = None


def test_ui_strings_integrity_raises():
    if UIStringManager is None:
        pytest.fail("UIStringManager not implemented yet")
    with pytest.raises(ValueError):
        UIStringManager({})
