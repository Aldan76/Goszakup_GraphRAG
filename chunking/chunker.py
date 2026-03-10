"""
Hierarchical text chunker for preserving document structure and semantics.
"""

import re
from typing import List, Tuple

from pydantic import BaseModel, Field


class ChunkStatistics(BaseModel):
    """Statistics about chunking operation."""

    total_characters: int = Field(..., description="Total input characters")
    total_chunks: int = Field(..., description="Total chunks created")
    average_chunk_size: float = Field(..., description="Average chunk size")
    min_chunk_size: int = Field(..., description="Minimum chunk size")
    max_chunk_size: int = Field(..., description="Maximum chunk size")
    total_overlap_characters: int = Field(..., description="Total characters in overlap regions")


class HierarchicalChunker:
    """
    Hierarchical text chunker that respects document structure.

    Strategy: Document → Sections → Paragraphs → Sentences → Tokens
    """

    def __init__(
        self,
        chunk_size: int = 500,
        overlap: int = 100,
        separator_pattern: str = r"\n\n+",  # Paragraph separator
    ):
        """
        Initialize chunker.

        Args:
            chunk_size: Target size for chunks (in characters)
            overlap: Size of overlap between chunks
            separator_pattern: Regex pattern for splitting text into sections
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.separator_pattern = separator_pattern

    def chunk(self, text: str) -> Tuple[List[str], ChunkStatistics]:
        """
        Split text into hierarchical chunks.

        Args:
            text: Input text to chunk

        Returns:
            Tuple of (chunks list, statistics)
        """
        if not text or len(text.strip()) == 0:
            return [], self._create_stats(text, 0, 0, 0)

        # Split into logical sections first
        sections = self._split_into_sections(text)

        chunks = []
        total_overlap = 0

        for section in sections:
            section_chunks, section_overlap = self._chunk_section(section)
            chunks.extend(section_chunks)
            total_overlap += section_overlap

        # Create statistics
        stats = self._create_stats(text, len(chunks), total_overlap, len(text))

        return chunks, stats

    def _split_into_sections(self, text: str) -> List[str]:
        """Split text into logical sections using separator pattern."""
        # First, remove extra whitespace
        text = re.sub(r" +", " ", text)

        # Split by separator pattern
        sections = re.split(self.separator_pattern, text)

        # Filter out empty sections
        return [s.strip() for s in sections if s.strip()]

    def _chunk_section(self, section: str) -> Tuple[List[str], int]:
        """
        Chunk a single section while preserving semantics.

        Returns:
            Tuple of (chunks, total_overlap_characters)
        """
        if len(section) <= self.chunk_size:
            return [section], 0

        # Try to split by sentences first
        sentences = self._split_into_sentences(section)

        if len(sentences) == 1:
            # Single long sentence - split by words
            return self._chunk_by_words(sentences[0])

        # Combine sentences into chunks
        chunks = []
        current_chunk = ""
        total_overlap = 0

        for sentence in sentences:
            # Check if adding this sentence exceeds chunk_size
            if len(current_chunk) + len(sentence) + 1 <= self.chunk_size:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                # Save current chunk
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())

                    # Calculate overlap for statistics
                    overlap_text = self._get_overlap_text(current_chunk)
                    total_overlap += len(overlap_text)

                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = overlap_text + " " + sentence if overlap_text else sentence

        # Add last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks, total_overlap

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting - can be improved with NLTK
        # Pattern: ends with . ! or ? followed by space and capital letter or end of string
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]

    def _chunk_by_words(self, text: str) -> Tuple[List[str], int]:
        """Fallback: chunk by words when no sentence boundaries found."""
        words = text.split()
        chunks = []
        current_chunk = ""
        total_overlap = 0

        for word in words:
            if len(current_chunk) + len(word) + 1 <= self.chunk_size:
                current_chunk += " " + word if current_chunk else word
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                    overlap_text = self._get_overlap_text(current_chunk)
                    total_overlap += len(overlap_text)
                    current_chunk = overlap_text + " " + word

        if current_chunk:
            chunks.append(current_chunk)

        return chunks, total_overlap

    def _get_overlap_text(self, text: str) -> str:
        """Get the overlap portion of text (last N characters)."""
        if len(text) <= self.overlap:
            return text
        # Try to get last complete words within overlap size
        words = text.split()
        overlap_words = []
        overlap_size = 0
        for word in reversed(words):
            if overlap_size + len(word) + 1 <= self.overlap:
                overlap_words.insert(0, word)
                overlap_size += len(word) + 1
            else:
                break
        return " ".join(overlap_words)

    def _create_stats(self, text: str, chunk_count: int, total_overlap: int, total_chars: int) -> ChunkStatistics:
        """Create statistics object."""
        avg_size = total_chars / chunk_count if chunk_count > 0 else 0
        min_size = self.chunk_size
        max_size = 0

        return ChunkStatistics(
            total_characters=total_chars,
            total_chunks=chunk_count,
            average_chunk_size=avg_size,
            min_chunk_size=min_size,
            max_chunk_size=max_size,
            total_overlap_characters=total_overlap,
        )
