import math
from collections import Counter
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class MemoryDocument(BaseModel):
    """Individual document or context object stored in long-term memory."""
    id: str
    content: str
    embedding: List[float] = Field(default_factory=list)
    metadata: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)


class SearchResult(BaseModel):
    """Object containing search results and score details."""
    document: MemoryDocument
    score: float
    rank: Optional[int] = None


class PersistentMemoryEngine:
    """
    RRF (Reciprocal Rank Fusion) based hybrid search and memory pruning engine.
    - Dense Search: Semantic search using cosine similarity
    - Sparse Search: Keyword matching using BM25 scoring
    - Rank Fusion: Unified reranking using the RRF algorithm
    """

    def __init__(self, rrf_k: int = 60):
        self.documents: Dict[str, MemoryDocument] = {}
        self.rrf_k = rrf_k

    def add_document(self, doc: MemoryDocument) -> None:
        """Add a document to long-term memory."""
        self.documents[doc.id] = doc

    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def _dense_search(self, query_vector: List[float], top_k: int) -> List[SearchResult]:
        """Perform dense vector similarity search."""
        results = []
        for doc in self.documents.values():
            sim = self._cosine_similarity(query_vector, doc.embedding)
            results.append(SearchResult(document=doc, score=sim))
        
        # Sort descending by similarity score
        results.sort(key=lambda x: x.score, reverse=True)
        for rank, res in enumerate(results[:top_k], start=1):
            res.rank = rank
        return results[:top_k]

    def _sparse_bm25_search(self, query: str, top_k: int) -> List[SearchResult]:
        """Perform sparse BM25 keyword search."""
        query_tokens = query.lower().split()
        if not query_tokens or not self.documents:
            return []

        # Corpus statistics
        doc_list = list(self.documents.values())
        N = len(doc_list)
        avgdl = sum(len(d.content.lower().split()) for d in doc_list) / N if N > 0 else 1.0

        # BM25 Parameters
        k1 = 1.5
        b = 0.75

        # Calculate IDF
        idf: Dict[str, float] = {}
        for token in set(query_tokens):
            n_q = sum(1 for d in doc_list if token in d.content.lower().split())
            idf[token] = math.log((N - n_q + 0.5) / (n_q + 0.5) + 1.0)

        results = []
        for doc in doc_list:
            doc_tokens = doc.content.lower().split()
            doc_len = len(doc_tokens)
            tf_counter = Counter(doc_tokens)
            
            score = 0.0
            for token in query_tokens:
                if token in tf_counter:
                    tf = tf_counter[token]
                    numerator = idf.get(token, 0.0) * tf * (k1 + 1)
                    denominator = tf + k1 * (1 - b + b * (doc_len / avgdl))
                    score += numerator / denominator

            results.append(SearchResult(document=doc, score=score))

        results.sort(key=lambda x: x.score, reverse=True)
        for rank, res in enumerate(results[:top_k], start=1):
            res.rank = rank
        return results[:top_k]

    def hybrid_search(
        self, query: str, query_vector: List[float], top_k: int = 5
    ) -> List[SearchResult]:
        """
        Merge Dense and Sparse search results using Reciprocal Rank Fusion (RRF).
        RRF Score(d) = sum(1 / (k + rank_m(d)))
        """
        dense_results = self._dense_search(query_vector, top_k=top_k * 2)
        sparse_results = self._sparse_bm25_search(query, top_k=top_k * 2)

        rrf_scores: Dict[str, float] = {}
        doc_map: Dict[str, MemoryDocument] = {}

        # Apply Dense RRF weights
        for res in dense_results:
            doc_id = res.document.id
            doc_map[doc_id] = res.document
            rank = res.rank or 1
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (self.rrf_k + rank))

        # Apply Sparse RRF weights
        for res in sparse_results:
            doc_id = res.document.id
            doc_map[doc_id] = res.document
            rank = res.rank or 1
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (self.rrf_k + rank))

        # Sort by consolidated RRF score
        combined_results = [
            SearchResult(document=doc_map[doc_id], score=score)
            for doc_id, score in rrf_scores.items()
        ]
        combined_results.sort(key=lambda x: x.score, reverse=True)

        for rank, res in enumerate(combined_results[:top_k], start=1):
            res.rank = rank

        return combined_results[:top_k]

    def prune_old_memories(self, max_capacity: int) -> int:
        """
        Prune oldest memories when memory capacity exceeds max_capacity.
        :return: Number of deleted documents
        """
        if len(self.documents) <= max_capacity:
            return 0

        excess_count = len(self.documents) - max_capacity
        sorted_docs = sorted(self.documents.values(), key=lambda d: d.created_at)

        deleted_count = 0
        for doc in sorted_docs[:excess_count]:
            del self.documents[doc.id]
            deleted_count += 1

        return deleted_count