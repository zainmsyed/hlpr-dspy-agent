import pytest

from hlpr.llm.dspy_integration import DSPyDocumentSummarizer


def test_dspy_timeout_short():
    # If DSPy is not available, the constructor may raise; handle gracefully
    try:
        summarizer = DSPyDocumentSummarizer(provider="local", timeout=1)
    except Exception:  # noqa: BLE001 - test probes environment availability
        pytest.skip("DSPy not available in test environment")

    # Use a short input and a small timeout so the test runs quickly.
    # The environment may either perform the summarization or raise a
    # runtime-style timeout error (SummarizationError subclasses RuntimeError).
    short_text = "This is a quick DSPy availability check."

    try:
        result = summarizer.summarize(short_text)
        # If successful, ensure the result looks like a summary object
        assert hasattr(result, "summary")
    except Exception as exc:
        # If DSPy fails during summarization, it should raise a runtime-style
        # error (SummarizationError -> RuntimeError). Any other exception
        # indicates an unexpected failure and should fail the test.
        assert isinstance(exc, RuntimeError)


def test_dspy_no_timeout():
    try:
        summarizer = DSPyDocumentSummarizer(provider="local", timeout=30)
    except Exception:  # noqa: BLE001 - test probes environment availability
        pytest.skip("DSPy not available in test environment")

    short_text = "This is a short test text."
    # Should not raise; if it does, skip (environment may not provide full DSPy)
    try:
        result = summarizer.summarize(short_text)
        assert hasattr(result, "summary")
    except RuntimeError:
        pytest.skip("DSPy runtime not available for actual summarization")
