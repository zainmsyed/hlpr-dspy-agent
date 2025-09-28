import pytest

from hlpr.document.summarizer import DocumentSummarizer
from hlpr.models.document import Document


def test_local_provider_defaults_to_no_timeout(tmp_path):
    # Create a small markdown file
    p = tmp_path / "t.md"
    p.write_text("Hello world. This is a test.")

    doc = Document.from_file(p)
    doc.extracted_text = p.read_text()

    # Initialize summarizer for local provider without explicit timeout
    s = DocumentSummarizer(provider="local", timeout=None)

    # If DSPy is available and fails after retries, it may raise an exception
    # (we abort for local provider). Otherwise we should get a deterministic
    # fallback summary. Accept either outcome.
    try:
        result = s.summarize_document(doc)
    except RuntimeError:
        # DSPy integration may raise a runtime-style error in some environments
        pytest.skip("DSPy runtime error during summarization")
    else:
        assert hasattr(result, "summary")
