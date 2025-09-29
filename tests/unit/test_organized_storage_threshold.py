import shutil

import pytest

from hlpr.exceptions import StorageError
from hlpr.io.organized_storage import OrganizedStorage


def test_min_free_bytes_threshold(monkeypatch, tmp_path):
    storage = OrganizedStorage(base_directory=tmp_path, min_free_bytes=50)

    class FakeDiskUsage:
        total = 100
        used = 60
        free = 40

    def fake_disk_usage(path):
        return FakeDiskUsage

    monkeypatch.setattr(shutil, "disk_usage", fake_disk_usage)

    with pytest.raises(StorageError) as exc:
        storage.ensure_directory_exists()

    assert exc.value.details is not None
    assert exc.value.details.get("available_bytes") == 40
    assert exc.value.details.get("required_bytes") == 50
