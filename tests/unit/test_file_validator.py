from pathlib import Path

from hlpr.utils.file_validation import FileValidator


def test_exists_and_readable(tmp_path: Path):
    p = tmp_path / "a.txt"
    p.write_text("hi", encoding="utf-8")
    assert FileValidator.exists(p)
    assert FileValidator.is_readable(p)


def test_validate_missing(tmp_path: Path):
    p = tmp_path / "missing.txt"
    msgs = FileValidator.validate(p)
    assert msgs and msgs[0].code == "not_found"


def test_validate_directory(tmp_path: Path):
    d = tmp_path / "dir"
    d.mkdir()
    msgs = FileValidator.validate(d, must_be_file=True)
    assert any(m.code == "not_file" for m in msgs)


def test_validate_unreadable(tmp_path: Path):
    p = tmp_path / "x.txt"
    p.write_text("content", encoding="utf-8")
    # make unreadable (best-effort; may be skipped on some platforms)
    try:
        p.chmod(0o000)
        msgs = FileValidator.validate(p)
        assert any(m.code in {"not_readable", "access_error"} for m in msgs)
    finally:
        # restore perms so tmp dir cleanup works
        p.chmod(0o600)
