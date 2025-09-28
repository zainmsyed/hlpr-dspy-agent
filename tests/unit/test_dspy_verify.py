import contextlib

import pytest

from hlpr.llm.dspy_integration import DSPyDocumentSummarizer


class _DummyResult:
    def __init__(self, verdict=None, evidence=None, confidence=None):
        self.verdict = verdict
        self.evidence = evidence
        self.confidence = confidence


def test_verify_claims_success(monkeypatch):
    summ = DSPyDocumentSummarizer(provider="local")

    # Mock _result_from_future to return a dummy object with expected attrs
    def fake_result_from_future(_future, _start_time: float):
        return _DummyResult(
            verdict="yes",
            evidence="Found in paragraph 2",
            confidence=0.87,
        )

    # Avoid mutating dspy.settings during unit tests; use a no-op context
    monkeypatch.setattr(
        DSPyDocumentSummarizer,
        "_dspy_context",
        lambda _: contextlib.nullcontext(),
    )
    monkeypatch.setattr(summ, "_result_from_future", fake_result_from_future)

    claims = ["Claim A", "Claim B"]
    results = summ.verify_claims("source text", claims)

    assert isinstance(results, list)
    assert len(results) == 2
    for r in results:
        assert r["model_supported"] is True
        assert pytest.approx(r["model_confidence"], rel=1e-3) == 0.87
        assert "Found in" in r["model_evidence"]


def test_verify_claims_timeout(monkeypatch):
    summ = DSPyDocumentSummarizer(provider="local")

    # Simulate timeout by raising an exception from _result_from_future
    def fake_result_from_future_timeout(_future, _start_time: float):
        msg = "timeout"
        raise RuntimeError(msg)

    monkeypatch.setattr(summ, "_result_from_future", fake_result_from_future_timeout)

    claims = ["Claim C"]
    results = summ.verify_claims("source text", claims)

    assert isinstance(results, list)
    assert len(results) == 1
    r = results[0]
    assert r["model_supported"] is None
    assert r["model_confidence"] is None
    assert r["model_evidence"] == ""


def test_verify_claims_malformed_output(monkeypatch):
    summ = DSPyDocumentSummarizer(provider="local")

    # Return object with non-stringable/malformed fields
    class BadObj:
        def __init__(self):
            self.verdict = None
            self.evidence = None
            self.confidence = "not-a-number"

    def fake_result_from_future_bad(_future, _start_time: float):
        return BadObj()

    monkeypatch.setattr(summ, "_result_from_future", fake_result_from_future_bad)

    results = summ.verify_claims("source text", ["Claim D"])
    assert len(results) == 1
    r = results[0]
    # Malformed verdict should map to None/safe defaults
    assert r["model_supported"] is None
    assert r["model_confidence"] is None
    assert r["model_evidence"] == ""
