"""DSPy integration for document summarization.

This module provides DSPy-based summarization capabilities with support for
multiple LLM providers and automatic prompt optimization.
"""

import contextlib
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from contextlib import contextmanager

import dspy
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Thread-safe DSPy configuration using context manager
_dspy_config_lock = None  # Removed global lock


class DSPySummaryResult(BaseModel):
    """Result from DSPy document summarization."""

    summary: str
    key_points: list[str]
    processing_time_ms: int


class DocumentSummarizationSignature(dspy.Signature):
    """DSPy signature for document summarization."""

    document_text: str = dspy.InputField(
        desc="The full text content of the document to summarize",
    )
    summary: str = dspy.OutputField(
        desc="A concise summary of the document's main content",
    )
    key_points: list[str] = dspy.OutputField(
        desc="List of key points extracted from the document",
    )


class DSPyDocumentSummarizer:
    """DSPy-based document summarization service.

    Provides optimized summarization using DSPy with support for multiple
    LLM providers including local, OpenAI, Anthropic, Groq, and Together AI.
    """

    def __init__(  # noqa: PLR0913 - public initializer keeps backward-compatible args
        self,
        provider: str = "local",
    model: str = "gemma3:latest",
        api_base: str | None = None,
        api_key: str | None = None,
        max_tokens: int = 8192,
        temperature: float = 0.3,
        timeout: int = 30,
        fast_fail_seconds: float | None = 1.0,
    ):
        """Initialize DSPy document summarizer.

        Args:
            provider: LLM provider ('local', 'openai', 'anthropic', 'groq', 'together')
            model: Model name to use
            api_base: Base URL for API (for local providers)
            api_key: API key for cloud providers
            max_tokens: Maximum tokens per request
            temperature: Sampling temperature
            timeout: Request timeout in seconds

        Raises:
            ValueError: If provider configuration is invalid
        """
        # Validate provider configuration
        self.validate_provider_config(provider, api_key, api_base)

        self.provider = provider
        self.model = model
        self.api_base = api_base
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout
        # Number of seconds to wait for an immediate response before
        # continuing to wait up to `timeout`. If None, don't attempt
        # the short fast-fail wait and wait for the full timeout.
        self.fast_fail_seconds = fast_fail_seconds

        # Store LM configuration for per-instance use
        self._lm_config = self._create_lm_config()
        self.summarizer = None  # Will be created on-demand

    def _create_lm_config(self) -> dspy.LM:
        """Create LM configuration for this instance."""
        if self.provider == "local":
            # Configure for local Ollama-compatible API
            api_base = self.api_base or "http://localhost:11434"
            return dspy.LM(
                model=f"ollama/{self.model}",
                api_base=api_base,
                api_key=self.api_key or "ollama",
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
        if self.provider == "openai":
            if not self.api_key:
                msg = "API key required for OpenAI provider"
                raise ValueError(msg)
            return dspy.LM(
                model=f"openai/{self.model}",
                api_key=self.api_key,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
        if self.provider == "anthropic":
            if not self.api_key:
                msg = "API key required for Anthropic provider"
                raise ValueError(msg)
            return dspy.LM(
                model=f"anthropic/{self.model}",
                api_key=self.api_key,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
        if self.provider == "groq":
            # Support for Groq API
            if not self.api_key:
                msg = "API key required for Groq provider"
                raise ValueError(msg)
            return dspy.LM(
                model=f"groq/{self.model}",
                api_key=self.api_key,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
        if self.provider == "together":
            # Support for Together AI
            if not self.api_key:
                msg = "API key required for Together AI provider"
                raise ValueError(msg)
            return dspy.LM(
                model=f"together/{self.model}",
                api_key=self.api_key,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
        supported_providers = [
            "local",
            "openai",
            "anthropic",
            "groq",
            "together",
        ]
        msg = (
            f"Unsupported provider: {self.provider}. Supported: {supported_providers}"
        )
        raise ValueError(msg)

    @contextmanager
    def _dspy_context(self):
        """Context manager for thread-safe DSPy configuration."""
        # Store the current DSPy configuration
        current_lm = getattr(dspy.settings, "lm", None)

        try:
            # Configure DSPy for this instance
            dspy.configure(lm=self._lm_config)
            yield
        finally:
            # Restore previous configuration
            if current_lm is not None:
                dspy.configure(lm=current_lm)
            else:
                # Clear configuration if none was set before
                dspy.configure(lm=None)

    def _get_summarizer(self) -> dspy.Predict:
        """Get or create the summarizer with proper configuration."""
        if self.summarizer is None:
            with self._dspy_context():
                self.summarizer = dspy.Predict(DocumentSummarizationSignature)
        return self.summarizer

    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """Get list of supported LLM providers.

        Returns:
            List of supported provider names
        """
        return ["local", "openai", "anthropic", "groq", "together"]

    @classmethod
    def validate_provider_config(
        cls,
        provider: str,
        api_key: str | None = None,
        api_base: str | None = None,  # noqa: ARG003
    ) -> bool:
        """Validate provider configuration.

        Args:
            provider: Provider name
            api_key: API key (required for cloud providers)
            api_base: API base URL (optional for local)

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        if provider not in cls.get_supported_providers():
            msg = f"Unsupported provider: {provider}"
            raise ValueError(msg)

        # Cloud providers require API key
        cloud_providers = ["openai", "anthropic", "groq", "together"]
        if provider in cloud_providers and not api_key:
            msg = f"API key required for {provider} provider"
            raise ValueError(msg)

        return True

    def test_connectivity(self) -> bool:
        """Test connectivity to the configured LLM provider.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Simple test prompt
            test_text = "Hello, this is a test."
            result = self.summarize(test_text)
            return len(result.summary.strip()) > 0
        except Exception:
            logger.exception("Provider connectivity test failed")
            return False

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
        start_time = time.time()

        def _call_summarizer():
            # Call the DSPy summarizer synchronously inside the worker
            with self._dspy_context():
                summarizer = self._get_summarizer()
                return summarizer(document_text=text)

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                max_attempts = 2
                result = None

                for attempt in range(1, max_attempts + 1):
                    future = executor.submit(_call_summarizer)

                    try:
                        # LOCAL provider: allow longer startup/warmup times.
                        # Do a short probe if configured to catch immediate
                        # deterministic failures (bad config). If the probe
                        # times out, wait without timeout to allow the local
                        # model to finish loading and respond.
                        if self.provider == "local":
                            if self.fast_fail_seconds is not None:
                                try:
                                    result = future.result(timeout=self.fast_fail_seconds)
                                except FutureTimeoutError:
                                    logger.info(
                                        "DSPy local summarizer taking longer than %.2fs; waiting without timeout",
                                        self.fast_fail_seconds,
                                    )
                                    result = future.result()
                            else:
                                result = future.result()

                        # Non-local providers: enforce configured timeout
                        elif self.fast_fail_seconds is None:
                            result = future.result(timeout=self.timeout)
                        else:
                            try:
                                result = future.result(timeout=self.fast_fail_seconds)
                            except FutureTimeoutError:
                                elapsed = time.time() - start_time
                                remaining = max(self.timeout - elapsed, 0.1)
                                logger.info(
                                    "DSPy summarizer taking longer than %.2fs; waiting up to %.2fs more before aborting",
                                    self.fast_fail_seconds,
                                    remaining,
                                )
                                try:
                                    result = future.result(timeout=remaining)
                                except FutureTimeoutError:
                                    with contextlib.suppress(Exception):
                                        future.cancel()

                                    processing_time_ms = int((time.time() - start_time) * 1000)
                                    msg = (
                                        "DSPy summarization did not complete within the "
                                        "configured timeout; aborting."
                                    )
                                    logger.warning(msg)
                                    raise RuntimeError(msg) from None

                        # If we got a result, break out of retry loop
                        if result is not None:
                            break

                    except Exception as exc:
                        # On failure, retry once (useful for transient errors)
                        logger.warning(
                            "DSPy summarization attempt %d failed: %s",
                            attempt,
                            exc,
                        )
                        if attempt == max_attempts:
                            # Re-raise the last exception to be handled by
                            # the outer exception handlers below
                            raise
                        # Otherwise, continue to the next attempt

            # Ensure key_points is a list
            key_points = result.key_points
            if isinstance(key_points, str):
                # Split by newlines or common separators
                key_points = [
                    point.strip()
                    for point in key_points.split("\n")
                    if point.strip()
                ]
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
            msg = "DSPy summarization failed"
            logger.exception(msg)
            # Preserve original exception context
            raise RuntimeError(msg) from e

    def optimize_prompts(self, examples: list[dict]) -> None:  # noqa: ARG002
        """Optimize summarization prompts using MIPRO.

        Args:
            examples: List of example documents with expected summaries
        """
        # This would use DSPy's MIPRO optimizer for prompt optimization
        # Implementation depends on specific optimization requirements
        logger.info("Prompt optimization not yet implemented")


def create_dspy_summarizer(
    provider: str = "local",
    model: str = "gemma3:latest",
    timeout: int = 30,
    **kwargs,
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
        **kwargs,
    )
