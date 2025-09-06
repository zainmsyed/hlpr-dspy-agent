
from src.workflows.documents.summarizer import DocumentSummarizer, DocumentSummarizationInput
from src.workflows.documents.models import Document
import tempfile
import os


def test_summarizer_fallback(monkeypatch):
    # Make OllamaClient.predict raise an exception to force fallback
    class FakeClient:
        def predict(self, *a, **k):
            raise RuntimeError("nope")
        def get_dspy_lm(self):
            raise RuntimeError("nope")

    s = DocumentSummarizer(ollama_client=FakeClient())
    text = "First sentence. Second sentence. Third sentence."
    out = s.run(text)
    assert "First sentence" in out


def test_summarizer_uses_ollama_when_available(monkeypatch):
    class FakeClient:
        def predict(self, prompt, **k):
            return {"result": "- point one\n- point two\n- point three"}
        def get_dspy_lm(self):
            raise RuntimeError("DSPy not available")  # Force fallback to predict method

    s = DocumentSummarizer(ollama_client=FakeClient())
    text = "Doc text"
    out = s.run(text)
    assert "point one" in out


def test_new_process_method():
    """Test the new process method with structured input/output."""
    class FakeClient:
        def predict(self, prompt, **k):
            return {"result": "Test summary"}
        def get_dspy_lm(self):
            raise RuntimeError("DSPy not available")  # Force fallback

    s = DocumentSummarizer(ollama_client=FakeClient())
    doc = Document(id="test", text="Test document content")
    input_obj = DocumentSummarizationInput(document=doc)
    result = s.process(input_obj)
    
    assert result.summary == "Test summary"
    assert isinstance(result.key_takeaways, list)
    assert isinstance(result.entities, list)
    assert isinstance(result.key_dates, list)
    assert result.confidence is not None


def test_process_file_txt():
    """Test processing a text file."""
    class FakeClient:
        def predict(self, prompt, **k):
            return {"result": "File summary"}
        def get_dspy_lm(self):
            raise RuntimeError("DSPy not available")

    s = DocumentSummarizer(ollama_client=FakeClient())
    
    # Create a temporary text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test document. It contains some text to summarize.")
        temp_file = f.name
    
    try:
        result = s.process_file(temp_file)
        assert result.summary == "File summary"
        assert result.processing_time is not None
        assert result.confidence is not None
    finally:
        os.unlink(temp_file)


def test_unsupported_file_format():
    """Test handling of unsupported file formats."""
    from src.workflows.documents.processor import DocumentProcessor
    
    # Create a temporary file with unsupported extension
    with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
        f.write(b"test content")
        temp_file = f.name
    
    try:
        # Should raise ValueError for unsupported format
        try:
            DocumentProcessor.extract_text_from_file(temp_file)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Unsupported file format" in str(e)
    finally:
        os.unlink(temp_file)
