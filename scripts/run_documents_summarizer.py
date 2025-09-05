"""Small runner to demo the DocumentSummarizer with the OllamaClient.

Usage:
    python scripts/run_documents_summarizer.py

This will use the environment variables OLLAMA_BASE_URL and OLLAMA_MODEL if set.
"""

from src.workflows.documents.summarizer import DocumentSummarizer

EXAMPLE_TEXT = (
    "This document describes the design of the hlpr project. It explains the modular workflow architecture, "
    "the use of local models via Ollama, and the privacy-first processing guarantees. The design emphasizes "
    "testability, small reusable components, and clear CLI tooling. Further sections discuss optimizations and "
    "deployment considerations."
)


def main():
    s = DocumentSummarizer()
    out = s.run(EXAMPLE_TEXT)
    print("--- Summary ---")
    print(out)


if __name__ == '__main__':
    main()
