from pathlib import Path

import pytest

from hlpr.document.parser import DocumentParser


def write_tmp(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_parse_text_file(tmp_path):
    p = tmp_path / "sample.txt"
    write_tmp(p, "Hello world\nThis is a test document.")

    text = DocumentParser.parse_file(p)
    assert "Hello world" in text
    assert "test document" in text


def test_parse_md_file(tmp_path):
    p = tmp_path / "sample.md"
    write_tmp(p, "# Title\n\nSome markdown content.")

    text = DocumentParser.parse_file(p)
    assert "Title" in text
    assert "markdown content" in text


def test_missing_file_raises(tmp_path):
    p = tmp_path / "does_not_exist.txt"
    with pytest.raises(FileNotFoundError):
        DocumentParser.parse_file(p)


def test_empty_file_raises(tmp_path):
    p = tmp_path / "empty.txt"
    write_tmp(p, "   \n\n   ")

    with pytest.raises(ValueError):
        DocumentParser.parse_file(p)


def test_unsupported_extension_raises(tmp_path):
    p = tmp_path / "file.xyz"
    write_tmp(p, "content")

    with pytest.raises(ValueError):
        DocumentParser.parse_file(p)
