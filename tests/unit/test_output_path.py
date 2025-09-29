from pathlib import Path

from hlpr.models.output_path import OutputPath


def test_output_path_validate_writable_creates_parent(tmp_path):
    doc = tmp_path / "doc.md"
    out = tmp_path / "outdir" / "summary.md"
    op = OutputPath(original_document_path=str(doc), custom_output_path=str(out), resolved_path=out)

    assert op.validate_writable() is True


def test_output_path_validate_writable_permission_error(tmp_path, monkeypatch):
    out = tmp_path / "blocked" / "summary.md"
    op = OutputPath(original_document_path=str(tmp_path / "doc.md"), custom_output_path=str(out), resolved_path=out)

    # Monkeypatch Path.mkdir to raise PermissionError for the blocked directory
    orig_mkdir = Path.mkdir

    def fake_mkdir(self, parents=False, exist_ok=False):
        if "blocked" in str(self):
            raise PermissionError("mock denied")
        return orig_mkdir(self, parents=parents, exist_ok=exist_ok)

    monkeypatch.setattr(Path, "mkdir", fake_mkdir)

    assert op.validate_writable() is False


def test_output_path_validate_writable_cleans_probe(tmp_path):
    doc = tmp_path / "doc.md"
    out = tmp_path / "summary.md"
    op = OutputPath(original_document_path=str(doc), custom_output_path=str(out), resolved_path=out)

    probe_path = out.parent / ".hlpr_write_test"
    assert probe_path.exists() is False

    assert op.validate_writable() is True

    assert probe_path.exists() is False
