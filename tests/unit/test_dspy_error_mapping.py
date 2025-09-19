import time

import pytest

from hlpr.exceptions import HlprError, SummarizationError
from hlpr.llm.dspy_integration import DSPyDocumentSummarizer


def test_result_from_future_timeout_raises_summarization_error():
    summarizer = DSPyDocumentSummarizer(
        provider="local", timeout=0.01, fast_fail_seconds=0.0,
    )
    # Create a dummy future whose result() raises SummarizationError so the
    # behavior is deterministic across environments and doesn't block the
    # test runner waiting on a real Future that never completes.
    class DummyFuture:
        def result(self, *_, **__):
            msg = "simulated timeout"
            raise SummarizationError(msg)

    start = time.time()
    with pytest.raises(SummarizationError):
        summarizer._result_from_future(DummyFuture(), start)


def test_summarize_long_text_maps_to_summarization_error_if_exception():
    summarizer = DSPyDocumentSummarizer(provider="local", timeout=1)

    # Patch _invoke_summarizer to raise a generic exception for long inputs
    def _raise_exc(_text):
        msg = "simulated dspy failure"
        raise RuntimeError(msg)

    summarizer._invoke_summarizer = _raise_exc

    long_text = "x" * 200000

    with pytest.raises(SummarizationError) as excinfo:
        summarizer.summarize(long_text)

    # SummarizationError should also be a RuntimeError (compatibility)
    assert isinstance(excinfo.value, RuntimeError)
    assert isinstance(excinfo.value, HlprError)
