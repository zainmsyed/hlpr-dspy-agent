"""Document summarization services using DSPy."""

import logging
import re
import time

from pydantic import BaseModel

from hlpr.document.chunker import DocumentChunker
from hlpr.document.progress import (
    ProcessingPhase,
    ProgressContext,
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
    hallucinations: list[str] = []
    hallucination_verification: list[dict] = []


class DocumentSummarizer:
    """Document summarization service using DSPy.

    Provides configurable summarization with support for different LLM providers
    and chunking strategies for large documents.
    """

    def __init__(  # noqa: PLR0913 - initializer exposes config knobs for UX
        self,
        provider: str = "local",
        model: str = "gemma3:latest",
        api_base: str | None = None,
        api_key: str | None = None,
        max_tokens: int = 8192,
        temperature: float = 0.3,
        timeout: int = 30,
        progress_tracker: ProgressTracker | None = None,
        *,
        no_fallback: bool = False,
        verify_hallucinations: bool = False,
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
        self.no_fallback = no_fallback
        self.verify_hallucinations_flag = verify_hallucinations

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
        except Exception:  # pragma: no cover - best-effort fallback
            # Log full exception information to aid debugging, then fall back.
            logger.exception(
                "DSPy initialization failed, falling back to local summarizer",
            )
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
            result = self._summarize_with_dspy(document)
        except Exception:  # pragma: no cover - fallback path
            logger.exception("Summarization via DSPy failed")
            return self._handle_summarization_failure(document)
        else:
            return result

    def _summarize_with_dspy(self, document: Document) -> SummaryResult:
        """Internal helper to perform DSPy summarization and verification.

        Factored out to reduce complexity of `summarize_document` for linting.
        """
        with ProgressContext(
            self.progress_tracker,
            ProcessingPhase.SUMMARIZING,
            items_total=1,
        ) as metrics:
            dspy_result = self.dspy_summarizer.summarize(document.extracted_text)
            metrics.items_processed = 1

            hallucinations = self._detect_hallucinations(
                document.extracted_text,
                dspy_result.summary,
            )

            result = SummaryResult(
                summary=dspy_result.summary,
                key_points=dspy_result.key_points,
                processing_time_ms=dspy_result.processing_time_ms,
                hallucinations=hallucinations,
            )

            # Optionally verify hallucinations (deterministic overlap verification)
            if self.verify_hallucinations_flag and hallucinations:
                result.hallucination_verification = self.verify_hallucinations(
                    document.extracted_text,
                    hallucinations,
                )

            return result

    def _handle_summarization_failure(self, document: Document) -> SummaryResult:
        """Handle DSPy summarization failure by falling back deterministically."""
        logger.info("Falling back to deterministic summarizer")
        result = self._fallback_summarize(document.extracted_text)
        result.hallucinations = self._detect_hallucinations(
            document.extracted_text, result.summary,
        )
        if self.verify_hallucinations_flag and result.hallucinations:
            result.hallucination_verification = self.verify_hallucinations(
                document.extracted_text,
                result.hallucinations,
            )
        return result


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
        except Exception:
            msg = (
                "Failed to summarize text using DSPy, falling back to local summarizer"
            )
            logger.exception(msg)
            result = self._fallback_summarize(text)
            result.hallucinations = self._detect_hallucinations(
                text, result.summary,
            )
            if self.verify_hallucinations_flag and result.hallucinations:
                result.hallucination_verification = (
                    self.verify_hallucinations(text, result.hallucinations)
                )
            return result
        else:
            summary_text = dspy_result.summary
            hallucinations = self._detect_hallucinations(
                document_text, summary_text,
            )
            result = SummaryResult(
                summary=dspy_result.summary,
                key_points=dspy_result.key_points,
                processing_time_ms=dspy_result.processing_time_ms,
                hallucinations=hallucinations,
            )
            if self.verify_hallucinations_flag and hallucinations:
                result.hallucination_verification = (
                    self.verify_hallucinations(document_text, hallucinations)
                )
            return result

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
        with ProgressContext(
            self.progress_tracker,
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
            with ProgressContext(
                self.progress_tracker,
                ProcessingPhase.SUMMARIZING,
                items_total=len(chunks),
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
                hallucinations=getattr(final_result, "hallucinations", []),
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
            hallucinations=[],
        )

    def _detect_hallucinations(self, source_text: str, summary_text: str) -> list[str]:
        """Lightweight hallucination detector using token overlap per sentence.

        For each sentence in the summary, compute overlap ratio with source
        text tokens. If ratio is below threshold, flag the sentence as
        potential hallucination. This is intentionally conservative and
        best-effort — it won't block summarization on error.
        """
        try:
            def tokenize(s: str) -> set[str]:
                return set(re.findall(r"\w+", s.lower()))

            source_tokens = tokenize(source_text)
            sentences = [
                s.strip()
                for s in re.split(r"(?<=[.!?])\s+", summary_text)
                if s.strip()
            ]
            flagged: list[str] = []
            threshold = 0.2

            for sent in sentences:
                sent_tokens = tokenize(sent)
                if not sent_tokens:
                    continue
                overlap = len(sent_tokens & source_tokens) / len(sent_tokens)
                if overlap < threshold:
                    flagged.append(sent)
        except Exception:  # pragma: no cover - failing safely
            logger.exception("Hallucination detector failed")
            return []
        else:
            return flagged

    def verify_hallucinations(
        self,
        source_text: str,
        hallucinations: list[str],
    ) -> list[dict]:
        """Verify flagged hallucination sentences using deterministic overlap metrics.

        This lightweight verifier returns, for each flagged sentence, an object
        with the sentence, overlap ratio, a conservative boolean indicating
        whether it appears supported by the source, and a small list of
        supporting tokens. The implementation is deterministic and cheap; a
        future version can replace this with a model-based verification step
        that emits evidence and model confidence scores.
        """
        results: list[dict] = []
        try:
            def tokenize(s: str) -> list[str]:
                return re.findall(r"\w+", s.lower())

            source_tokens = set(tokenize(source_text))

            for sent in hallucinations:
                sent_tokens = tokenize(sent)
                if not sent_tokens:
                    results.append(
                        {
                            "sentence": sent,
                            "overlap": 0.0,
                            "likely_supported": False,
                            "supporting_tokens": [],
                        },
                    )
                    continue

                sent_set = set(sent_tokens)
                overlap_count = len(sent_set & source_tokens)
                overlap_ratio = overlap_count / len(sent_set)

                # Conservative threshold: consider supported if >= 0.3 overlap
                likely_supported = overlap_ratio >= 0.3

                results.append(
                    {
                        "sentence": sent,
                        "overlap": overlap_ratio,
                        "likely_supported": likely_supported,
                        "supporting_tokens": list(sent_set & source_tokens),
                    },
                )
        except Exception:  # pragma: no cover - failing safely
            logger.exception("Hallucination verification failed")
            return []
        else:
            return results
