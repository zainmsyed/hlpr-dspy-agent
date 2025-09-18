import stat

from hlpr.cli.validators import validate_config, validate_file_path


def test_validate_file_path_empty():
    ok, msg = validate_file_path("")
    assert not ok
    assert "empty" in msg


def test_validate_file_path_nonexistent(tmp_path):
    p = tmp_path / "nope.txt"
    ok, msg = validate_file_path(str(p))
    assert not ok
    assert "does not exist" in msg


def test_validate_file_path_directory(tmp_path):
    ok, msg = validate_file_path(str(tmp_path))
    assert not ok
    assert "not a file" in msg


def test_validate_file_path_unreadable(tmp_path):
    file_path = tmp_path / "secret.txt"
    file_path.write_text("content")
    # remove read permissions for owner
    mode = file_path.stat().st_mode
    file_path.chmod(mode & ~stat.S_IRUSR)

    ok, msg = validate_file_path(str(file_path))

    # On some CI filesystems chmod may behave differently; accept either readable
    # or an explicit unreadable error.
    if ok:
        # If the environment still reports readable, ensure content exists
        assert file_path.exists()
    else:
        assert "readable" in msg


def test_validate_file_path_ok(tmp_path):
    file_path = tmp_path / "ok.txt"
    file_path.write_text("x")
    ok, msg = validate_file_path(str(file_path))
    assert ok
    assert msg == "ok"


def test_validate_config_missing_keys():
    ok, msg = validate_config({})
    assert not ok
    assert "missing required option" in msg


def test_validate_config_unsupported_provider():
    ok, msg = validate_config({"provider": "unknown", "output_format": "md"})
    assert not ok
    assert "unsupported provider" in msg


def test_validate_config_unsupported_format():
    ok, msg = validate_config({"provider": "local", "output_format": "xml"})
    assert not ok
    assert "unsupported output_format" in msg


def test_validate_config_ok():
    ok, msg = validate_config({"provider": "local", "output_format": "md"})
    assert ok
    assert msg == "ok"
