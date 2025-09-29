from hlpr.config.storage import DEFAULT_MIN_FREE_BYTES
from hlpr.models.output_preferences import OutputPreferences


def test_output_preferences_default_min_free_bytes():
    prefs = OutputPreferences()
    assert prefs.min_free_bytes == DEFAULT_MIN_FREE_BYTES


def test_output_preferences_override_min_free_bytes():
    prefs = OutputPreferences(min_free_bytes=1234)
    assert prefs.min_free_bytes == 1234

