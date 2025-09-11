import pytest
from hlpr.document.chunker import Chunker


def test_chunker_basic():
    text = """
    This is the first sentence. This is the second sentence. This is the third sentence.
    """
    c = Chunker(chunk_size=50, overlap=10)
    chunks = c.chunk_text(text)
    assert len(chunks) >= 1
    assert all(isinstance(ch, str) for ch in chunks)


def test_chunker_empty():
    c = Chunker(chunk_size=50, overlap=10)
    assert c.chunk_text("") == []


def test_chunker_invalid_params():
    with pytest.raises(ValueError):
        Chunker(chunk_size=10, overlap=20)
