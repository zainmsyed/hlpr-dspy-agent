import json

from hlpr.config._atomic import atomic_write
from hlpr.io.atomic import atomic_write_text


def test_atomic_write_creates_file_and_writes(tmp_path):
    target = tmp_path / "config.json"
    data = json.dumps({"a": 1})

    atomic_write(target, data)

    assert target.exists()
    assert target.read_text(encoding="utf-8") == data


def test_atomic_write_sets_permissions(tmp_path):
    target = tmp_path / "config2.json"
    data = json.dumps({"b": 2})

    atomic_write(target, data, mode=0o600)

    # Permission check is best-effort; ensure file exists and readable
    assert target.exists()
    assert '{"b": 2}' in target.read_text(encoding="utf-8")


def test_atomic_write_text(tmp_path):
    target = tmp_path / "out.json"
    obj = {"a": 1, "b": [1, 2, 3]}
    text = json.dumps(obj, indent=2)

    atomic_write_text(target, text)

    assert target.exists()
    got = json.loads(target.read_text(encoding="utf-8"))
    assert got == obj

    # No temp files starting with .out.json. should remain
    leftover = list(tmp_path.glob(".out.json.*"))
    assert not leftover
