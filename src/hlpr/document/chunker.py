"""Chunking utilities for large document processing."""

from typing import List
from pathlib import Path
import re


def split_into_sentences(text: str) -> List[str]:
    # Very small sentence splitter that's good enough for chunk boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


class Chunker:
    """Chunker class providing hierarchical and overlap-aware chunking.

    Default behavior works on characters and sentence boundaries.
    """

    def __init__(self, chunk_size: int = 4000, overlap: int = 200):
        if chunk_size <= overlap:
            raise ValueError("chunk_size must be greater than overlap")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks trying to respect sentence boundaries.

        Args:
            text: Full text to chunk

        Returns:
            List of text chunks
        """
        if not text:
            return []

        sentences = split_into_sentences(text)
        chunks = []
        current = []
        current_len = 0

        for s in sentences:
            s_len = len(s)
            # If adding this sentence would exceed chunk_size, flush current chunk
            if current_len + s_len + 1 > self.chunk_size:
                chunk_text = " ".join(current).strip()
                if chunk_text:
                    chunks.append(chunk_text)

                # Start new chunk, include overlap from previous chunk end
                # Calculate overlap content
                overlap_text = " ".join(current)[-self.overlap:]
                current = [overlap_text] if overlap_text else []
                current_len = len(overlap_text)

            current.append(s)
            current_len += s_len + 1

        # Flush final chunk
        if current:
            chunks.append(" ".join(current).strip())

        return chunks


def chunk_file(path: Path, chunk_size: int = 4000, overlap: int = 200) -> List[str]:
    """Read a file and chunk its content."""
    text = path.read_text(encoding="utf-8")
    c = Chunker(chunk_size=chunk_size, overlap=overlap)
    return c.chunk_text(text)
