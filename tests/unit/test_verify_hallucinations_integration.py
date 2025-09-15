import types

import dspy

from hlpr.document.summarizer import DocumentSummarizer


def test_verify_hallucinations_merges_model_results(monkeypatch):
    # Mock dspy.Predict to return different verdicts per claim
    def fake_predict(_signature):
        def call(*_args, **kwargs):
            claim = kwargs.get("claim", "")
            if "A" in claim:
                return types.SimpleNamespace(
                    verdict="yes",
                    evidence="evidence A",
                    confidence="0.9",
                )
            return types.SimpleNamespace(verdict="no", evidence="", confidence="0.1")

        return call

    monkeypatch.setattr(dspy, "Predict", fake_predict)

    summarizer = DocumentSummarizer(
        provider="local",
        model="gemma3:latest",
        verify_hallucinations=True,
    )

    source = "This document mentions Alice and Bob."
    # craft hallucination sentences that deterministic detector will flag
    hallucinations = ["Alice invented the protocol A.", "Charlie built system B."]

    results = summarizer.verify_hallucinations(source, hallucinations)

    assert isinstance(results, list)
    assert len(results) == 2
    # Check merged fields exist
    for r in results:
        assert "model_supported" in r
        assert "model_confidence" in r
        assert "model_evidence" in r
