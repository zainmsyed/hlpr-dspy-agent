
from src.workflows.documents.summarizer import DocumentSummarizer


def test_summarizer_fallback(monkeypatch):
    # Make OllamaClient.predict raise an exception to force fallback
    class FakeClient:
        def predict(self, *a, **k):
            raise RuntimeError("nope")

    s = DocumentSummarizer(ollama_client=FakeClient())
    text = "First sentence. Second sentence. Third sentence."
    out = s.run(text)
    assert "First sentence" in out


def test_summarizer_uses_ollama_when_available(monkeypatch):
    class FakeClient:
        def predict(self, prompt, **k):
            return {"result": "- point one\n- point two\n- point three"}

    s = DocumentSummarizer(ollama_client=FakeClient())
    text = "Doc text"
    out = s.run(text)
    assert "point one" in out
