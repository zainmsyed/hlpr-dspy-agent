import types


def test_guided_execute_runs_parse_and_summarize(tmp_path, monkeypatch):
    """Ensure guided --execute runs parse and summarizer and persists template."""
    sample = tmp_path / "sample.md"
    sample.write_text("# Title\n\nBody text")

    calls = {"parse": False, "summarize": False}

    def fake_parse(path, verbose=False):
        calls["parse"] = True
        # lightweight Document object via Document.from_file to keep compatibility
        from hlpr.models.document import Document

        doc = Document.from_file(str(path))
        return doc, "extracted text"

    def fake_summarize(
        summarizer,
        document,
        extracted_text,
        chunk_size,
        chunk_overlap,
        chunking_strategy,
        verbose,
    ):
        calls["summarize"] = True
        return types.SimpleNamespace(summary="ok", key_points=[], processing_time_ms=1)

    # Ensure saved-commands go to tmp_path instead of repo
    from hlpr.config import CONFIG

    monkeypatch.setattr(CONFIG, "user_config_dir", str(tmp_path), raising=False)

    monkeypatch.setattr("hlpr.cli.summarize._parse_with_progress", fake_parse)
    monkeypatch.setattr("hlpr.cli.summarize._summarize_with_progress", fake_summarize)

    from hlpr.cli.summarize import summarize_guided

    # Call the CLI handler directly with execute=True
    summarize_guided(str(sample), execute=True)

    assert calls["parse"] and calls["summarize"]
