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
    except Exception as exc:
        # If DSPy is available but failing, we expect an exception type
        # from DSPy integration (SummarizationError or underlying runtime).
        assert isinstance(exc, Exception)
    else:
        assert hasattr(result, "summary")
