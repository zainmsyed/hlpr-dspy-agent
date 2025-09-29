import os
import stat
import shutil
from pathlib import Path

import pytest

from hlpr.io.organized_storage import OrganizedStorage
from hlpr.exceptions import StorageError


def test_ensure_directory_creates_base(tmp_path):
    storage = OrganizedStorage(base_directory=tmp_path)
    base = storage.get_organized_base()
    assert not base.exists()
    created = storage.ensure_directory_exists()
    assert created.exists()
    assert created == base


def test_permission_error_raises(tmp_path):
    # Create a directory and remove write permissions to simulate permission error
    protected = tmp_path / "protected_base"
    protected.mkdir()
    # Remove write permissions for owner
    protected.chmod(stat.S_IREAD)

    storage = OrganizedStorage(base_directory=protected.parent, summaries_folder=str(protected.name))

    try:
        with pytest.raises(StorageError):
            storage.ensure_directory_exists()
    finally:
        # Restore permissions so pytest can clean up the tmpdir
        protected.chmod(stat.S_IRWXU)


def test_min_free_bytes_check(tmp_path, monkeypatch):
    storage = OrganizedStorage(base_directory=tmp_path)
    # Force an extremely large min_free_bytes to trigger insufficient space
    storage.min_free_bytes = 10 ** 18

    with pytest.raises(StorageError):
        storage.ensure_directory_exists()
import re
import shutil
from pathlib import Path

import pytest

from hlpr.config.storage import MAX_FILENAME_STEM_LENGTH, SAFE_FILENAME_PATTERN
from hlpr.exceptions import StorageError
from hlpr.io.organized_storage import OrganizedStorage


def test_get_organized_path_basic(tmp_path):
    storage = OrganizedStorage(base_directory=tmp_path)
    doc = "documents/examples/cover_letter.md"
    p = storage.get_organized_path(doc)
    assert p.name.endswith("_summary.md")
    assert "hlpr" in str(p)


def test_generate_filename_blocks_traversal(tmp_path):
    storage = OrganizedStorage(base_directory=tmp_path)
    fname = storage.generate_filename("../../../../etc/passwd", "md")

    assert ".." not in fname
    assert "/" not in fname
    assert fname.endswith("_summary.md")


def test_generate_filename_truncates_long_names(tmp_path):
    storage = OrganizedStorage(base_directory=tmp_path)
    long_name = "a" * 300 + ".txt"
    fname = storage.generate_filename(long_name, "txt")

    stem = fname.rsplit(".", 1)[0]
    # stem includes "_summary" suffix, so subtract it before comparison
    sanitized = stem.removesuffix("_summary")
    assert len(sanitized) <= MAX_FILENAME_STEM_LENGTH


def test_generate_filename_sanitizes_invalid_chars(tmp_path):
    storage = OrganizedStorage(base_directory=tmp_path)
    name = "inv@lid:name?.txt"

    fname = storage.generate_filename(name, "txt")
    stem = fname.rsplit(".", 1)[0].removesuffix("_summary")

    forbidden = re.compile(SAFE_FILENAME_PATTERN)
    assert forbidden.search(stem) is None


def test_generate_filename_uses_uuid_when_empty(tmp_path):
    storage = OrganizedStorage(base_directory=tmp_path)
    name = "!!!.md"

    fname = storage.generate_filename(name)

    stem = fname.rsplit(".", 1)[0].removesuffix("_summary")
    # sanitized stem should fall back to summary_<uuid>
    assert stem.startswith("summary_")
    assert len(stem) > len("summary_")


def test_ensure_directory_exists_low_disk(monkeypatch, tmp_path):
    storage = OrganizedStorage(base_directory=tmp_path)

    class FakeDiskUsage:
        total = 100
        used = 99
        free = 0

    def fake_disk_usage(path):
        return FakeDiskUsage

    monkeypatch.setattr(shutil, "disk_usage", fake_disk_usage)

    with pytest.raises(StorageError) as exc:
        storage.ensure_directory_exists()

    assert "Insufficient disk space" in str(exc.value)


def test_ensure_directory_exists_permission_error(tmp_path, monkeypatch):
    storage = OrganizedStorage(base_directory=tmp_path)
    base = storage.get_organized_base()

    # Make a directory and then make it unreadable/unwritable
    base.mkdir(parents=True, exist_ok=True)

    # Monkeypatch Path.mkdir to raise a PermissionError when called for this base
    orig_mkdir = Path.mkdir

    def fake_mkdir(self, parents=False, exist_ok=False):
        if str(self) == str(base):
            raise PermissionError("Mock permission denied")
        return orig_mkdir(self, parents=parents, exist_ok=exist_ok)

    monkeypatch.setattr(Path, "mkdir", fake_mkdir)

    with pytest.raises(StorageError):
        storage.ensure_directory_exists()
