"""
Embeddings management for RAG queries and documents.
Uses sentence-transformers for local embeddings generation.
"""

import hashlib
import logging
from typing import List, Optional

from sentence_transformers import SentenceTransformer

from config.settings import settings

logger = logging.getLogger(__name__)


class EmbeddingsManager:
    """Manages embeddings generation and caching."""

    def __init__(self, model: Optional[str] = None, cache_enabled: bool = True):
        """
        Initialize embeddings manager.

        Args:
            model: Sentence-transformers model name (default from settings)
            cache_enabled: Whether to cache embeddings
        """
        self.model_name = model or settings.embeddings_model
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded embeddings model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load embeddings model: {e}")
            # Fallback to smaller model
            self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self.model = SentenceTransformer(self.model_name)

        self.cache_enabled = cache_enabled
        self._embedding_cache = {}

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.md5(text.encode()).hexdigest()

    def embed_text(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for text using sentence-transformers.

        Args:
            text: Text to embed

        Returns:
            Embedding vector or None if failed
        """
        if not text:
            return None

        # Check cache
        cache_key = self._get_cache_key(text)
        if self.cache_enabled and cache_key in self._embedding_cache:
            logger.debug(f"Cache hit for embedding: {cache_key[:8]}")
            return self._embedding_cache[cache_key]

        try:
            # sentence-transformers returns numpy array, convert to list
            embedding = self.model.encode(text.strip(), convert_to_tensor=False).tolist()

            # Cache embedding
            if self.cache_enabled:
                self._embedding_cache[cache_key] = embedding

            logger.debug(f"Generated embedding for text ({len(text)} chars)")
            return embedding

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None

    def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        embeddings = []

        for text in texts:
            embedding = self.embed_text(text)
            embeddings.append(embedding)

        logger.info(f"Generated {len([e for e in embeddings if e])} embeddings out of {len(texts)}")
        return embeddings

    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score (0-1)
        """
        import math

        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        magnitude1 = math.sqrt(sum(a * a for a in embedding1))
        magnitude2 = math.sqrt(sum(b * b for b in embedding2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def clear_cache(self) -> None:
        """Clear embedding cache."""
        self._embedding_cache.clear()
        logger.info("Embedding cache cleared")

    def get_cache_size(self) -> int:
        """Get number of cached embeddings."""
        return len(self._embedding_cache)
