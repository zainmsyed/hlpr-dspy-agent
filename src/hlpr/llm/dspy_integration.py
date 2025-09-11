"""DSPy integration for document summarization.

This module provides DSPy-based summarization capabilities with support for
multiple LLM providers and automatic prompt optimization.
"""

import logging
from typing import List, Optional

import dspy
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Thread-safe DSPy configuration
from threading import Lock
_dspy_config_lock = Lock()


class DSPySummaryResult(BaseModel):
    """Result from DSPy document summarization."""

    summary: str
    key_points: List[str]
    processing_time_ms: int


class DocumentSummarizationSignature(dspy.Signature):
    """DSPy signature for document summarization."""

    document_text: str = dspy.InputField(desc="The full text content of the document to summarize")
    summary: str = dspy.OutputField(desc="A concise summary of the document's main content")
    key_points: List[str] = dspy.OutputField(desc="List of key points extracted from the document")


class DSPyDocumentSummarizer:
    """DSPy-based document summarization service.

    Provides optimized summarization using DSPy with support for multiple
    LLM providers and automatic prompt refinement.
    """

    def __init__(
        self,
        provider: str = "local",
        model: str = "llama3.2",
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
        max_tokens: int = 8192,
        temperature: float = 0.3,
        timeout: int = 30,
    ):
        """Initialize DSPy document summarizer.

        Args:
            provider: LLM provider ('local', 'openai', 'anthropic')
            model: Model name to use
            api_base: Base URL for API (for local providers)
            api_key: API key for cloud providers
            max_tokens: Maximum tokens per request
            temperature: Sampling temperature
            timeout: Request timeout in seconds
        """
        self.provider = provider
        self.model = model
        self.api_base = api_base
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._configure_dspy()
        self.summarizer = dspy.Predict(DocumentSummarizationSignature)

    def _configure_dspy(self) -> None:
        """Configure DSPy with the specified provider."""
        with _dspy_config_lock:
            if self.provider == "local":
                # Configure for local Ollama-compatible API
                api_base = self.api_base or "http://localhost:11434"
                lm = dspy.LM(
                    model=f"ollama/{self.model}",
                    api_base=api_base,
                    api_key=self.api_key or "ollama",
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
            elif self.provider == "openai":
                lm = dspy.LM(
                    model=f"openai/{self.model}",
                    api_key=self.api_key,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
            elif self.provider == "anthropic":
                lm = dspy.LM(
                    model=f"anthropic/{self.model}",
                    api_key=self.api_key,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

            dspy.configure(lm=lm)

    def summarize(self, text: str) -> DSPySummaryResult:
        """Summarize document text using DSPy with a cross-platform timeout.

        Uses a ThreadPoolExecutor to run the DSPy predict call in a worker
        thread and enforces a timeout using Future.result(timeout=...). This
        approach is thread-safe and works on Windows and Unix.

        Args:
            text: Document text to summarize

        Returns:
            DSPySummaryResult with summary and key points
        """
        import time
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

        start_time = time.time()

        def _call_summarizer():
            # Call the DSPy summarizer synchronously inside the worker
            return self.summarizer(document_text=text)

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_call_summarizer)
                try:
                    result = future.result(timeout=self.timeout)
                except FutureTimeoutError:
                    processing_time_ms = int((time.time() - start_time) * 1000)
                    logger.error(f"DSPy summarization timed out after {self.timeout} seconds")
                    raise RuntimeError(f"DSPy summarization timed out after {self.timeout} seconds")

            # Ensure key_points is a list
            key_points = result.key_points
            if isinstance(key_points, str):
                # Split by newlines or common separators
                key_points = [point.strip() for point in key_points.split('\n') if point.strip()]
            elif not isinstance(key_points, list):
                key_points = [str(key_points)]

            # Filter empty points
            key_points = [point for point in key_points if point.strip()]

            processing_time_ms = int((time.time() - start_time) * 1000)

            return DSPySummaryResult(
                summary=result.summary.strip(),
                key_points=key_points,
                processing_time_ms=processing_time_ms,
            )

        except RuntimeError:
            # Re-raise runtime errors (including timeout)
            raise
        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            logger.error(f"DSPy summarization failed: {e}")
            raise RuntimeError(f"DSPy summarization failed: {e}")

    def optimize_prompts(self, examples: List[dict]) -> None:
        """Optimize summarization prompts using MIPRO.

        Args:
            examples: List of example documents with expected summaries
        """
        # This would use DSPy's MIPRO optimizer for prompt optimization
        # Implementation depends on specific optimization requirements
        logger.info("Prompt optimization not yet implemented")
        pass


def create_dspy_summarizer(
    provider: str = "local",
    model: str = "llama3.2",
    timeout: int = 30,
    **kwargs
) -> DSPyDocumentSummarizer:
    """Factory function to create DSPy document summarizer.

    Args:
        provider: LLM provider
        model: Model name
        timeout: Request timeout in seconds
        **kwargs: Additional configuration options

    Returns:
        Configured DSPyDocumentSummarizer instance
    """
    return DSPyDocumentSummarizer(
        provider=provider,
        model=model,
        timeout=timeout,
        **kwargs
    )