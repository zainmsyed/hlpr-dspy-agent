import pytest

try:
    from hlpr.config.ui_strings import UIStringKeys, UIStringManager
except Exception:  # noqa: BLE001
    UIStringManager = None
    UIStringKeys = None


def test_ui_string_manager_integrity_and_get():
    if UIStringManager is None:
        pytest.fail("UIStringManager not implemented yet")
    strings = {
        "validation.empty_path": "Empty path",
        "validation.file_not_found": "File not found: {path}",
        "prompts.select_provider": "Select provider",
        "errors.config_corrupted": "Config corrupted",
        "success.config_saved": "Saved"
    }
    with pytest.raises(ValueError):
        UIStringManager({})

    um = UIStringManager(strings)
    s = um.get("validation.file_not_found", path="/no")
    assert "/no" in s
