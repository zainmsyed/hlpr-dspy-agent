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
        # Prefer fresh model runs for summarization/verification by
        # disabling the LM-level cache for this instance when possible.
        # This prevents reusing previous responses during iterative tests.
        # Some dspy LM implementations expose a `cache` attribute
        # (teleprompt utilities toggle this in tests). Prefer to disable
        # it for fresh runs; suppress any errors if the attribute is
        # unavailable or not writable.
        # Attempt attribute assignment if available; suppress exceptions
        with contextlib.suppress(Exception):
            if hasattr(self._lm_config, "cache"):
                self._lm_config.cache = False
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

    def _invoke_summarizer(self, text: str):
        """Invoke the DSPy summarizer within the configured context."""
        with self._dspy_context():
            summarizer = self._get_summarizer()
            return summarizer(document_text=text)

    def _result_from_future(self, future, start_time: float):
        """Handle waiting on a future with provider-specific semantics.

        Extracted from the main summarize() method to reduce cyclomatic
        complexity and allow focused unit testing.
        """
        # LOCAL provider: allow longer startup/warmup times.
        if self.provider == "local":
            if self.fast_fail_seconds is not None:
                try:
                    return future.result(timeout=self.fast_fail_seconds)
                except FutureTimeoutError:
                    logger.info(
                        "Local summarizer busy; waiting without timeout",
                    )
                    return future.result()
            return future.result()

        # Non-local providers: enforce configured timeout
        if self.fast_fail_seconds is None:
            return future.result(timeout=self.timeout)

        try:
            return future.result(timeout=self.fast_fail_seconds)
        except FutureTimeoutError:
            elapsed = time.time() - start_time
            remaining = max(self.timeout - elapsed, 0.1)
            logger.info(
                "Summarizer slow; will wait up to %.2fs more before aborting",
                remaining,
            )
            try:
                return future.result(timeout=remaining)
            except FutureTimeoutError:
                with contextlib.suppress(Exception):
                    future.cancel()

                msg = (
                    "DSPy summarization did not complete within the configured "
                    "timeout; aborting."
                )
                logger.warning(msg)
                raise RuntimeError(msg) from None

    @staticmethod
    def _normalize_key_points(key_points):
        """Normalize key_points into a list of non-empty strings.

        Accepts str, list, or other types and returns a cleaned list.
        """
        if isinstance(key_points, str):
            return [point.strip() for point in key_points.split("\n") if point.strip()]
        if isinstance(key_points, list):
            return [str(p).strip() for p in key_points if str(p).strip()]
        return [str(key_points)]

    class VerificationSignature(dspy.Signature):
        """DSPy signature for claim verification.

        Inputs:
            source_text: full document or excerpt
            claim: the sentence/claim to verify

        Outputs:
            verdict: 'yes'|'no'|'uncertain'
            evidence: supporting text excerpt (optional)
            confidence: numeric confidence 0..1 (optional)
        """

        source_text: str = dspy.InputField(desc="Source document text")
        claim: str = dspy.InputField(desc="Claim to verify")
        verdict: str = dspy.OutputField(desc="yes|no|uncertain")
        evidence: str = dspy.OutputField(desc="Supporting evidence excerpt")
        confidence: float = dspy.OutputField(desc="Confidence 0..1")

    def verify_claims(self, source_text: str, claims: list[str]) -> list[dict]:
        """Model-backed verification for a list of claims.

        For each claim, runs a DSPy Predict using `VerificationSignature` and
        returns a dict with keys: claim, model_supported (bool|None),
        model_confidence (float|None), model_evidence (str).

        This is best-effort and will return conservative defaults on failure.
        """
        results: list[dict] = []
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                for claim in claims:
                    def _call_verifier(claim=claim):
                        with self._dspy_context():
                            verifier = dspy.Predict(self.VerificationSignature)
                            return verifier(source_text=source_text, claim=claim)

                    future = executor.submit(_call_verifier)
                    try:
                        start_time = time.time()
                        # use a short per-claim timeout
                        raw = self._result_from_future(future, start_time)
                    except Exception:
                        logger.exception("Model-backed verification failed for a claim")
                        results.append(
                            {
                                "claim": claim,
                                "model_supported": None,
                                "model_confidence": None,
                                "model_evidence": "",
                            },
                        )
                        continue

                    # Parse model outputs conservatively
                    verdict = getattr(raw, "verdict", "uncertain")
                    evidence = getattr(raw, "evidence", "")
                    confidence = getattr(raw, "confidence", None)

                    model_supported = None
                    if isinstance(verdict, str):
                        v = verdict.strip().lower()
                        if v in ("yes", "supported", "true"):
                            model_supported = True
                        elif v in ("no", "unsupported", "false"):
                            model_supported = False

                    # Attempt to normalize confidence
                    try:
                        conf_val = (
                            float(confidence) if confidence is not None else None
                        )
                    except (ValueError, TypeError) as exc:
                        # tolerant parsing: non-numeric confidence will be ignored
                        logger.debug("Could not parse confidence: %s", exc)
                        conf_val = None

                    results.append(
                        {
                            "claim": claim,
                            "model_supported": model_supported,
                            "model_confidence": conf_val,
                            "model_evidence": evidence or "",
                        },
                    )
        except Exception:  # pragma: no cover - best-effort
            logger.exception("verify_claims failed")
            return [
                {
                    "claim": c,
                    "model_supported": None,
                    "model_confidence": None,
                    "model_evidence": "",
                }
                for c in claims
            ]
        else:
            return results

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
            return self._invoke_summarizer(text)

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                max_attempts = 2
                result = None

                for attempt in range(1, max_attempts + 1):
                    future = executor.submit(_call_summarizer)
                    try:
                        result = self._result_from_future(future, start_time)
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

            # Normalize key_points into a clean list
            key_points = self._normalize_key_points(result.key_points)

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
