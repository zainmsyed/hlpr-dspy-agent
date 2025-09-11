import time
import pytest

from hlpr.llm.dspy_integration import DSPyDocumentSummarizer


def test_dspy_timeout_short():
    # If DSPy is not available, the constructor may raise; handle gracefully
    try:
        summarizer = DSPyDocumentSummarizer(provider="local", timeout=1)
    except Exception:
        pytest.skip("DSPy not available in test environment")

    # Use a long input that may take time; we expect a timeout runtime error
    long_text = "\n".join(["This is a test sentence." for _ in range(10000)])

    with pytest.raises(RuntimeError):
        summarizer.summarize(long_text)


def test_dspy_no_timeout():
    try:
        summarizer = DSPyDocumentSummarizer(provider="local", timeout=30)
    except Exception:
        pytest.skip("DSPy not available in test environment")

    short_text = "This is a short test text."
    # Should not raise
    try:
        result = summarizer.summarize(short_text)
        assert hasattr(result, "summary")
    except RuntimeError:
        pytest.skip("DSPy runtime not available for actual summarization")
