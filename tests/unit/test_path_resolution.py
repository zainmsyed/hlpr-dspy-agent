from hlpr.io.organized_storage import OrganizedStorage


def test_sanitized_filename_and_length(tmp_path):
    storage = OrganizedStorage(base_directory=tmp_path)

    # Very long and unsafe name should be sanitized and truncated
    unsafe_name = "a" * 300 + "<>:\\/*?|"
    filename = storage.generate_filename(unsafe_name, format="md")

    assert filename.endswith("_summary.md")
    stem = filename.split("_summary.md")[0]
    # Ensure it's not longer than configured max stem length
    from hlpr.config.storage import MAX_FILENAME_STEM_LENGTH

    assert len(stem) <= MAX_FILENAME_STEM_LENGTH
    # Sanitization should remove unsafe characters
    assert all(c.isalnum() or c in "_-" for c in stem)


def test_generate_filename_default_format(tmp_path):
    storage = OrganizedStorage(base_directory=tmp_path)
    fname = storage.generate_filename("/path/to/document.txt", None)
    assert fname.endswith(".md")
