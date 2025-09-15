import os
import time

import pytest

from hlpr.document.parser import DocumentParser
from hlpr.document.summarizer import DocumentSummarizer
from hlpr.models.document import Document

pytestmark = pytest.mark.integration


def _should_run_perf() -> bool:
    return os.environ.get("PYTEST_PERF", "0") == "1"


@pytest.mark.skipif(not _should_run_perf(), reason="Performance tests disabled")
def test_parsing_and_summarization_performance(tmp_path):
    # Prepare a small text document
    p = tmp_path / "perf.txt"
    content = """
    This is a short document used to exercise the parser and summarizer.
    It contains multiple sentences. The goal is a quick run under 2 seconds.
    """
    p.write_text(content, encoding="utf-8")

    # Measure parse + summarize
    start = time.time()
    text = DocumentParser.parse_file(p)
    doc = Document.from_file(p)
    doc.extracted_text = text

    summarizer = DocumentSummarizer()
    # Force using the local deterministic fallback to avoid external DSPy delays
    summarizer.use_dspy = False
    summarizer.dspy_summarizer = None
    result = summarizer.summarize_document(doc)
    elapsed = time.time() - start

    # Basic sanity checks
    assert result.summary
    assert isinstance(result.processing_time_ms, int)

    # Performance assertion (relaxed to 2 seconds for small local runs)
    assert elapsed < 2.0, f"Parsing+summarization took too long: {elapsed:.2f}s"
