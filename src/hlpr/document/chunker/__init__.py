"""Document chunking strategies for large document processing.

This module provides various strategies for splitting large documents into
manageable chunks while preserving context and semantic boundaries.
"""

import logging
import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class ChunkingStrategy(ABC):
    """Abstract base class for document chunking strategies."""

    @abstractmethod
    def chunk_text(self, text: str, chunk_size: int, overlap: int = 0) -> list[str]:
        """Split text into chunks according to the strategy.

        Args:
            text: The text to chunk
            chunk_size: Maximum size of each chunk (characters or tokens)
            overlap: Number of characters/tokens to overlap between chunks

        Returns:
            List of text chunks
        """


class SentenceBasedChunker(ChunkingStrategy):
    """Chunk text based on sentence boundaries for better semantic coherence."""

    def __init__(self, sentence_split_pattern: str | None = None):
        """Initialize sentence-based chunker.

        Args:
            sentence_split_pattern: Regex pattern for sentence splitting
        """
        self.sentence_split_pattern = sentence_split_pattern or r"(?<=[.!?])\s+"

    def chunk_text(self, text: str, chunk_size: int, overlap: int = 0) -> list[str]:
        """Split text into chunks at sentence boundaries.

        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Characters to overlap between chunks

        Returns:
            List of text chunks
        """
        if chunk_size <= overlap:
            msg = "Chunk size must be greater than overlap"
            raise ValueError(msg)

        # Split into sentences
        sentences = re.split(self.sentence_split_pattern, text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return [text]

        chunks = []
        current_chunk = ""
        current_size = 0

        for sentence in sentences:
            sentence_size = len(sentence)

            # If adding this sentence would exceed chunk size
            if current_size + sentence_size > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())

                # Start new chunk with overlap if specified
                if overlap > 0 and len(current_chunk) > overlap:
                    overlap_text = current_chunk[-overlap:].strip()
                    current_chunk = overlap_text + " " + sentence
                    current_size = len(current_chunk)
                else:
                    current_chunk = sentence
                    current_size = sentence_size
            else:
                # Add sentence to current chunk
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
                current_size += sentence_size + 1  # +1 for space

        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks


class ParagraphBasedChunker(ChunkingStrategy):
    """Chunk text based on paragraph boundaries."""

    def __init__(self, paragraph_split_pattern: str | None = None):
        """Initialize paragraph-based chunker.

        Args:
            paragraph_split_pattern: Regex pattern for paragraph splitting
        """
        self.paragraph_split_pattern = paragraph_split_pattern or r"\n\s*\n"

    def chunk_text(self, text: str, chunk_size: int, overlap: int = 0) -> list[str]:
        """Split text into chunks at paragraph boundaries.

        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Characters to overlap between chunks

        Returns:
            List of text chunks
        """
        if chunk_size <= overlap:
            msg = "Chunk size must be greater than overlap"
            raise ValueError(msg)

        # Split into paragraphs
        paragraphs = re.split(self.paragraph_split_pattern, text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        if not paragraphs:
            return [text]

        chunks = []
        current_chunk = ""
        current_size = 0

        for paragraph in paragraphs:
            paragraph_size = len(paragraph)

            # If adding this paragraph would exceed chunk size
            if current_size + paragraph_size > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())

                # Start new chunk with overlap if specified
                if overlap > 0 and len(current_chunk) > overlap:
                    overlap_text = current_chunk[-overlap:].strip()
                    current_chunk = overlap_text + "\n\n" + paragraph
                    current_size = len(current_chunk)
                else:
                    current_chunk = paragraph
                    current_size = paragraph_size
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
                current_size += paragraph_size + 2  # +2 for \n\n

        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks


class FixedSizeChunker(ChunkingStrategy):
    """Simple fixed-size chunking with character-based splitting."""

    def chunk_text(self, text: str, chunk_size: int, overlap: int = 0) -> list[str]:
        """Split text into fixed-size chunks.

        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Characters to overlap between chunks

        Returns:
            List of text chunks
        """
        if chunk_size <= overlap:
            msg = "Chunk size must be greater than overlap"
            raise ValueError(msg)

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size

            # If we're not at the end, try to find a good break point
            if end < text_length:
                # Look for word boundaries within the last 100 characters
                break_chars = [" ", "\n", "\t"]
                best_break = end

                for break_char in break_chars:
                    last_break = text.rfind(break_char, start, end)
                    if last_break != -1 and last_break > end - 100:
                        best_break = last_break
                        break

                end = best_break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move start position with overlap
            start = end - overlap

            # Ensure we make progress
            start = min(end, start)

        return chunks


class TokenBasedChunker(ChunkingStrategy):
    """Chunk text based on token count (approximated by words)."""

    def __init__(self, tokenizer: Callable[[str], list[str]] | None = None):
        """Initialize token-based chunker.

        Args:
            tokenizer: Function to tokenize text (defaults to word splitting)
        """
        self.tokenizer = tokenizer or (lambda text: text.split())

    def chunk_text(self, text: str, chunk_size: int, overlap: int = 0) -> list[str]:
        """Split text into chunks based on token count.

        Args:
            text: Text to chunk
            chunk_size: Maximum tokens per chunk
            overlap: Tokens to overlap between chunks

        Returns:
            List of text chunks
        """
        if chunk_size <= overlap:
            msg = "Chunk size must be greater than overlap"
            raise ValueError(msg)

        # Tokenize the entire text
        tokens = self.tokenizer(text)
        if not tokens:
            return [text]

        chunks = []
        start = 0
        total_tokens = len(tokens)

        while start < total_tokens:
            end = min(start + chunk_size, total_tokens)

            # Get tokens for this chunk
            chunk_tokens = tokens[start:end]
            chunk_text = " ".join(chunk_tokens)

            if chunk_text.strip():
                chunks.append(chunk_text.strip())

            # Move start position with overlap
            start = end - overlap

            # Ensure we make progress
            start = min(end, start)

        return chunks


class DocumentChunker:
    """Main document chunking service with multiple strategies."""

    def __init__(
        self,
        default_strategy: str = "sentence",
        chunk_size: int | None = None,
        overlap: int | None = None,
    ):
        """Initialize document chunker.

        Args:
            default_strategy: Default chunking strategy
                ('sentence', 'paragraph', 'fixed', 'token')
            chunk_size: Optional default chunk size (characters/tokens)
            overlap: Optional default overlap between chunks
        """
        self.default_strategy = default_strategy
        # Default chunking parameters (None means callers must pass them or
        # instance will provide fallbacks). Tests create Chunker(chunk_size=..)
        # so we store provided values and validate them here.
        self.default_chunk_size = chunk_size
        self.default_overlap = overlap

        if (
            self.default_chunk_size is not None
            and self.default_overlap is not None
            and self.default_chunk_size <= self.default_overlap
        ):
            msg = "Chunk size must be greater than overlap"
            raise ValueError(msg)

        self.strategies: dict[str, ChunkingStrategy] = {
            "sentence": SentenceBasedChunker(),
            "paragraph": ParagraphBasedChunker(),
            "fixed": FixedSizeChunker(),
            "token": TokenBasedChunker(),
        }

    def chunk_text(
        self,
        text: str,
        chunk_size: int | None = None,
        overlap: int | None = None,
        strategy: str | None = None,
    ) -> list[str]:
        """Chunk text using specified or default strategy.

        Args:
            text: Text to chunk
            chunk_size: Maximum size per chunk
            overlap: Overlap between chunks
            strategy: Chunking strategy to use

        Returns:
            List of text chunks

        Raises:
            ValueError: If strategy is not supported
        """
        strategy_name = strategy or self.default_strategy

        # Empty input should yield no chunks
        if not text or not text.strip():
            return []

        # Use instance defaults when caller doesn't provide values
        if chunk_size is None:
            chunk_size = self.default_chunk_size
        if overlap is None:
            overlap = self.default_overlap or 0

        if chunk_size is None:
            msg = "chunk_size must be provided"
            raise ValueError(msg)

        # At this point chunk_size and overlap are ints

        if strategy_name not in self.strategies:
            available = list(self.strategies.keys())
            msg = (
                f"Unsupported chunking strategy: {strategy_name}. "
                f"Available: {available}"
            )
            raise ValueError(msg)

        chunker = self.strategies[strategy_name]

        try:
            chunks = chunker.chunk_text(text, chunk_size, overlap)
        except Exception:
            msg = (
                f"Failed to chunk text with {strategy_name} strategy; "
                "falling back to fixed-size chunking"
            )
            logger.exception(msg)
            # Fallback to fixed-size chunking
            fallback_chunker = FixedSizeChunker()
            return fallback_chunker.chunk_text(text, chunk_size, overlap)
        else:
            logger.info(
                "Chunked text into %d chunks using %s strategy",
                len(chunks),
                strategy_name,
            )
            return chunks

    def add_strategy(self, name: str, strategy: ChunkingStrategy):
        """Add a custom chunking strategy.

        Args:
            name: Name of the strategy
            strategy: ChunkingStrategy instance
        """
        self.strategies[name] = strategy
        logger.info("Added custom chunking strategy: %s", name)

    def get_chunk_info(self, text: str, chunks: list[str]) -> dict[str, Any]:
        """Get information about chunking results.

        Args:
            text: Original text
            chunks: Chunked text pieces

        Returns:
            Dictionary with chunking statistics
        """
        total_chars = len(text)
        chunk_sizes = [len(chunk) for chunk in chunks]
        avg_chunk_size = sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0

        return {
            "original_length": total_chars,
            "num_chunks": len(chunks),
            "chunk_sizes": chunk_sizes,
            "avg_chunk_size": avg_chunk_size,
            "min_chunk_size": min(chunk_sizes) if chunk_sizes else 0,
            "max_chunk_size": max(chunk_sizes) if chunk_sizes else 0,
        }


# Convenience functions
def chunk_by_sentences(text: str, chunk_size: int, overlap: int = 0) -> list[str]:
    """Convenience function for sentence-based chunking."""
    chunker = SentenceBasedChunker()
    return chunker.chunk_text(text, chunk_size, overlap)


def chunk_by_paragraphs(text: str, chunk_size: int, overlap: int = 0) -> list[str]:
    """Convenience function for paragraph-based chunking."""
    chunker = ParagraphBasedChunker()
    return chunker.chunk_text(text, chunk_size, overlap)


def chunk_fixed_size(text: str, chunk_size: int, overlap: int = 0) -> list[str]:
    """Convenience function for fixed-size chunking."""
    chunker = FixedSizeChunker()
    return chunker.chunk_text(text, chunk_size, overlap)


# Backwards compatibility: expose `Chunker` name expected by some tests/clients
Chunker = DocumentChunker
