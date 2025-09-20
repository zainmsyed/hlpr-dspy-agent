#!/usr/bin/env python3
"""Demo script to exercise the full DSPy -> local LLM (Ollama) path.

This mirrors the `/summarize/document` endpoint flow but runs synchronously
from the repo so we can demonstrate DSPy output without starting the API.
"""
import json
import logging
import time
from pathlib import Path

from hlpr.document.parser import DocumentParser
from hlpr.document.summarizer import DocumentSummarizer
from hlpr.models.document import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("demo_dspy")

FILE = Path(__file__).resolve().parents[1] / "test_document.txt"


def main():
    start = time.time()
    logger.info("Parsing file: %s", FILE)
    extracted = DocumentParser.parse_file(str(FILE))

    doc = Document.from_file(str(FILE))
    doc.extracted_text = extracted

    logger.info("Initializing DocumentSummarizer (provider=local)")
    summarizer = DocumentSummarizer(provider="local")

    logger.info("Calling DSPy summarizer...")
    try:
        result = summarizer.summarize_document(doc)
    except Exception:
        logger.exception("DSPy summarization failed")
        # Try fallback deterministic summarizer
        logger.info("Falling back to the local summarizer...")
        result = summarizer.summarize_text(doc.extracted_text)

    payload = {
        "summary": result.summary,
        "key_points": result.key_points,
        "processing_time_ms": result.processing_time_ms,
        "total_time_ms": int((time.time() - start) * 1000),
    }

    logger.info(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
