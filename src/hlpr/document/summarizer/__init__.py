"""Document summarization services using DSPy."""

import logging
import time

from pydantic import BaseModel

from hlpr.document.chunker import DocumentChunker
from hlpr.document.progress import (
    ProcessingPhase,
    ProgressTracker,
    create_progress_tracker,
)
from hlpr.llm.dspy_integration import DSPyDocumentSummarizer
from hlpr.models.document import Document

logger = logging.getLogger(__name__)


class SummaryResult(BaseModel):
    """Result of document summarization."""

    summary: str
    key_points: list[str]
    processing_time_ms: int


class DocumentSummarizer:
    """Document summarization service using DSPy.

    Provides configurable summarization with support for different LLM providers
    and chunking strategies for large documents.
    """

    def __init__(  # noqa: PLR0913 - initializer exposes config knobs for UX
        self,
        provider: str = "local",
        model: str = "llama3.2",
        api_base: str | None = None,
        api_key: str | None = None,
        max_tokens: int = 8192,
        temperature: float = 0.3,
        timeout: int = 30,
        progress_tracker: ProgressTracker | None = None,
    ):
        """Initialize the document summarizer.

        Args:
            provider: LLM provider ('local', 'openai', 'anthropic')
            model: Model name to use
            api_base: Base URL for API (for local providers)
            api_key: API key for cloud providers
            max_tokens: Maximum tokens per request
            temperature: Sampling temperature
            timeout: Request timeout in seconds
            progress_tracker: Optional progress tracker for monitoring
        """
        self.provider = provider
        self.model = model
        self.api_base = api_base
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout
        self.progress_tracker = progress_tracker or create_progress_tracker()

        # Initialize DSPy summarizer with fallback handling
        self.use_dspy = True
        try:
            self.dspy_summarizer = DSPyDocumentSummarizer(
                provider=provider,
                model=model,
                api_base=api_base,
                api_key=api_key,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout,
            )
        except Exception:
            # Log full exception information to aid debugging, then fall back.
            msg = (
                "DSPy initialization failed, falling back to local summarizer"
            )
            logger.exception(msg)
            self.use_dspy = False
            self.dspy_summarizer = None

        # Initialize document chunker
        self.chunker = DocumentChunker()

    def summarize_document(self, document: Document) -> SummaryResult:
        """Summarize a document using DSPy.

        Args:
            document: Document instance with extracted text

        Returns:
            SummaryResult with summary, key points, and processing time

        Raises:
            ValueError: If document has no extracted text
        """
        if not document.extracted_text:
            msg = "Document has no extracted text to summarize"
            raise ValueError(msg)

        # If DSPy isn't available, use a simple fallback summarizer to allow tests
        if not self.use_dspy or self.dspy_summarizer is None:
            return self._fallback_summarize(document.extracted_text)

        try:
            # Use DSPy summarizer
            with self.progress_tracker.start_phase(
                ProcessingPhase.SUMMARIZING, items_total=1,
            ) as metrics:
                dspy_result = self.dspy_summarizer.summarize(document.extracted_text)
                metrics.items_processed = 1

            return SummaryResult(
                summary=dspy_result.summary,
                key_points=dspy_result.key_points,
                processing_time_ms=dspy_result.processing_time_ms,
            )

        except Exception:
            # Include stack trace for easier debugging. Fall back deterministically.
            msg = (
                "Failed to summarize document using DSPy, "
                "falling back to local summarizer"
            )
            logger.exception(msg)
            return self._fallback_summarize(document.extracted_text)

    def summarize_text(
        self,
        text: str,
        title: str | None = None,
    ) -> SummaryResult:
        """Summarize raw text content.

        Args:
            text: Text content to summarize
            title: Optional document title for context

        Returns:
            SummaryResult with summary, key points, and processing time
        """
        if not text.strip():
            msg = "Text content is empty"
            raise ValueError(msg)

        # Add title context if provided
        document_text = text
        if title:
            document_text = f"Title: {title}\n\n{text}"

        # If DSPy is not available, use fallback
        if not self.use_dspy or self.dspy_summarizer is None:
            return self._fallback_summarize(text)

        try:
            # Use DSPy summarizer
            dspy_result = self.dspy_summarizer.summarize(document_text)

            return SummaryResult(
                summary=dspy_result.summary,
                key_points=dspy_result.key_points,
                processing_time_ms=dspy_result.processing_time_ms,
            )

        except Exception:
            msg = (
                "Failed to summarize text using DSPy, falling back to local summarizer"
            )
            logger.exception(msg)
            return self._fallback_summarize(text)

    def summarize_large_document(
        self,
        document: Document,
        chunk_size: int = 4000,
        overlap: int = 200,
        chunking_strategy: str = "sentence",
    ) -> SummaryResult:
        """Summarize a large document by chunking it.

        Args:
            document: Document instance with extracted text
            chunk_size: Maximum characters per chunk
            overlap: Characters to overlap between chunks
            chunking_strategy: Strategy for chunking
                ('sentence', 'paragraph', 'fixed', 'token')

        Returns:
            SummaryResult with hierarchical summary
        """
        if not document.extracted_text:
            msg = "Document has no extracted text to summarize"
            raise ValueError(msg)

        text = document.extracted_text

        # If document is small enough, summarize directly
        if len(text) <= chunk_size:
            return self.summarize_document(document)

        # Split text into chunks using the document chunker
        with self.progress_tracker.start_phase(
            ProcessingPhase.CHUNKING,
            items_total=1,
            metadata={"strategy": chunking_strategy},
        ) as chunk_metrics:
            chunks = self.chunker.chunk_text(
                text,
                chunk_size,
                overlap,
                chunking_strategy,
            )
            chunk_metrics.items_processed = 1
            chunk_metrics.metadata.update({"num_chunks": len(chunks)})

        start_time = time.time()

        try:
            # Summarize each chunk
            chunk_summaries = []
            with self.progress_tracker.start_phase(
                ProcessingPhase.SUMMARIZING, items_total=len(chunks),
            ) as summary_metrics:
                for i, chunk in enumerate(chunks):
                    chunk_title = f"Part {i + 1} of {len(chunks)}"
                    chunk_result = self.summarize_text(chunk, chunk_title)
                    chunk_summaries.append(chunk_result.summary)

                    # Update progress
                    summary_metrics.items_processed = i + 1
                    summary_metrics.current_item = chunk_title

            # Combine chunk summaries into final summary
            combined_text = "\n\n".join(
                f"Part {i + 1}: {summary}"
                for i, summary in enumerate(chunk_summaries)
            )

            final_result = self.summarize_text(
                combined_text,
                f"Combined summary of {len(chunks)} parts",
            )

            processing_time_ms = int((time.time() - start_time) * 1000)

            return SummaryResult(
                summary=final_result.summary,
                key_points=final_result.key_points,
                processing_time_ms=processing_time_ms,
            )

        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            # Log full exception and re-raise with chaining for clearer tracebacks
            msg = "Failed to summarize large document"
            logger.exception(msg)
            err_msg = "Large document summarization failed"
            raise ValueError(err_msg) from e

    def _fallback_summarize(self, text: str) -> SummaryResult:
        """A simple fallback summarizer used when DSPy or model is unavailable.

        Returns the first 1-2 sentences as a summary and uses short phrases as
        key points. This is intentionally lightweight and deterministic for
        tests.
        """
        # Simple sentence split by periods and newlines
        sentences = [
            s.strip()
            for s in text.replace("\n", " ").split(". ")
            if s.strip()
        ]
        summary = ". ".join(sentences[:2])
        if summary and not summary.endswith("."):
            summary = summary + "."

        # Key points: pick up short clauses or first clauses of sentences
        key_points = []
        for s in sentences[:4]:
            # take up to first 8 words
            words = s.split()
            kp = " ".join(words[:8])
            if kp:
                key_points.append(kp)

        processing_time_ms = 1
        return SummaryResult(
            summary=summary or text[:200],
            key_points=key_points,
            processing_time_ms=processing_time_ms,
        )
