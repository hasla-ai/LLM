import math
import time
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class CacheEntry(BaseModel):
    """Cached response entry with query embedding and metadata."""
    cache_id: str
    query_text: str
    embedding: List[float]
    response_text: str
    model_id: str
    tenant_id: str
    timestamp: float = Field(default_factory=time.time)


class CacheHitResult(BaseModel):
    """Metadata payload returned when a semantic cache lookup succeeds."""
    is_hit: bool
    similarity_score: float
    cached_response: Optional[str] = None
    original_query: Optional[str] = None


class SemanticCacheEngine:
    """
    Mission 39: Cross-Model Semantic Caching & Vector Similarity Deduplication Mesh.
    Provides fast vector-similarity lookups to serve pre-computed LLM responses.
    """

    def __init__(self, similarity_threshold: float = 0.90):
        self.similarity_threshold = similarity_threshold
        self._cache: List[CacheEntry] = []

    def set(
        self,
        cache_id: str,
        query_text: str,
        embedding: List[float],
        response_text: str,
        model_id: str,
        tenant_id: str
    ) -> CacheEntry:
        """Stores a query, its vector embedding, and response payload into the semantic cache."""
        entry = CacheEntry(
            cache_id=cache_id,
            query_text=query_text,
            embedding=embedding,
            response_text=response_text,
            model_id=model_id,
            tenant_id=tenant_id
        )
        self._cache.append(entry)
        return entry

    def get(
        self,
        query_embedding: List[float],
        tenant_id: Optional[str] = None
    ) -> CacheHitResult:
        """
        Performs vector cosine similarity search across cached query embeddings.
        Returns highest matching response if similarity exceeds threshold.
        """
        if not self._cache:
            return CacheHitResult(is_hit=False, similarity_score=0.0)

        best_score = -1.0
        best_entry: Optional[CacheEntry] = None

        for entry in self._cache:
            # Tenant isolation filter if provided
            if tenant_id and entry.tenant_id != tenant_id:
                continue

            score = self._cosine_similarity(query_embedding, entry.embedding)
            if score > best_score:
                best_score = score
                best_entry = entry

        if best_entry and best_score >= self.similarity_threshold:
            return CacheHitResult(
                is_hit=True,
                similarity_score=round(best_score, 4),
                cached_response=best_entry.response_text,
                original_query=best_entry.query_text
            )

        return CacheHitResult(
            is_hit=False,
            similarity_score=round(max(best_score, 0.0), 4)
        )

    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Computes cosine similarity between two vector lists."""
        if len(vec_a) != len(vec_b) or not vec_a:
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        return dot_product / (norm_a * norm_b)