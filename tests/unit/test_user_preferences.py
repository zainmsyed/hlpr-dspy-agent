
from hlpr.models.user_preferences import PreferencesStore, UserPreferences


def test_preferences_save_load(tmp_path):
    p = tmp_path / "prefs.json"
    store = PreferencesStore(path=p)
    prefs = UserPreferences(theme="dark", last_provider="local", last_format="rich")
    store.save(prefs)

    loaded = store.load()
    assert loaded.theme == "dark"
    assert loaded.last_provider == "local"
    assert loaded.last_format == "rich"


def test_load_nonexistent_returns_defaults(tmp_path):
    p = tmp_path / "missing.json"
    store = PreferencesStore(path=p)
    loaded = store.load()
    assert loaded.theme == "default"
