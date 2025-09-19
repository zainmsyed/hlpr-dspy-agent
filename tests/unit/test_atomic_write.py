import json

from hlpr.io.atomic import atomic_write_text


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
