import time
from concurrent.futures import Future

import pytest

from hlpr.llm.dspy_integration import DSPyDocumentSummarizer
from hlpr.exceptions import SummarizationError, HlprError


def test_result_from_future_timeout_raises_summarization_error():
    summarizer = DSPyDocumentSummarizer(provider="local", timeout=0.01, fast_fail_seconds=0.0)

    # Create a future that never completes
    future = Future()

    start = time.time()
    with pytest.raises(SummarizationError):
        summarizer._result_from_future(future, start)


def test_summarize_long_text_maps_to_summarization_error_if_exception():
    summarizer = DSPyDocumentSummarizer(provider="local", timeout=1)

    # Patch _invoke_summarizer to raise a generic exception for long inputs
    def _raise_exc(text):
        raise RuntimeError("simulated dspy failure")

    summarizer._invoke_summarizer = _raise_exc

    long_text = "x" * 200000

    with pytest.raises(SummarizationError) as excinfo:
        summarizer.summarize(long_text)

    # SummarizationError should also be a RuntimeError (compatibility)
    assert isinstance(excinfo.value, RuntimeError)
    assert isinstance(excinfo.value, HlprError)
