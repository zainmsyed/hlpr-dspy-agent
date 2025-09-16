# ruff: noqa: SLF001
import contextlib
import types

import dspy

from hlpr.llm.dspy_integration import DSPyDocumentSummarizer


def test_normalize_key_points_with_str():
    # Accessing a utility method for testing purposes; keep stable
    got = DSPyDocumentSummarizer._normalize_key_points(
        "point one\npoint two\n",
    )
    assert isinstance(got, list)
    assert got == ["point one", "point two"]


def test_normalize_key_points_with_list():
    got = DSPyDocumentSummarizer._normalize_key_points([" a ", "", "b"])
    assert got == ["a", "b"]


def test_verify_claims_with_mocked_predict(monkeypatch):
    # Prepare a fake predict callable that returns an object with
    # verdict/evidence/confidence
    def fake_predict(_signature):
        def call(*_args, **_kwargs):
            # Return a simple namespace mimicking DSPy output
            return types.SimpleNamespace(
                verdict="yes",
                evidence="found",
                confidence="0.85",
            )

        return call

    monkeypatch.setattr(dspy, "Predict", fake_predict)
    # Avoid mutating dspy.settings during unit tests; use a no-op context
    monkeypatch.setattr(
        DSPyDocumentSummarizer, "_dspy_context", lambda _: contextlib.nullcontext(),
    )

    summarizer = DSPyDocumentSummarizer(provider="local", model="gemma3:latest")

    claims = ["Claim A", "Claim B"]
    results = summarizer.verify_claims("some source text", claims)

    assert isinstance(results, list)
    assert len(results) == 2
    for r in results:
        assert r["claim"] in claims
        assert r["model_supported"] is True
        assert isinstance(r["model_confidence"], float)
        assert r["model_evidence"] == "found"
