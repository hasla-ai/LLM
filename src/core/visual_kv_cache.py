import time
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class VisualTokenCacheEntry(BaseModel):
    """Metadata and cached tensor key-value representation for visual embeddings."""
    cache_key: str
    doc_id: str
    page_number: int
    token_count: int
    kv_tensor_ref: str  # Simulated pointer to GPU/pinned host memory buffer
    last_accessed_at: float = Field(default_factory=time.time)
    access_count: int = 1


class VisualKVCacheEngine:
    """
    Mission 31: KV-Cache Multi-Modal Visual Context Retention Engine.
    Manages prefix-cached visual tokens across multi-turn sessions to eliminate image re-encoding latency.
    """

    def __init__(self, max_token_capacity: int = 32768):
        self.max_token_capacity = max_token_capacity
        self.current_token_usage = 0
        self.cache: Dict[str, VisualTokenCacheEntry] = {}

    def _generate_cache_key(self, doc_id: str, page_number: int) -> str:
        return f"{doc_id}_p{page_number}"

    def get_visual_tokens(self, doc_id: str, page_number: int) -> Optional[VisualTokenCacheEntry]:
        """Retrieves cached KV tensors for a given document page and updates access metrics."""
        cache_key = self._generate_cache_key(doc_id, page_number)
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            entry.last_accessed_at = time.time()
            entry.access_count += 1
            return entry
        return None

    def store_visual_tokens(
        self,
        doc_id: str,
        page_number: int,
        token_count: int,
        kv_tensor_ref: str
    ) -> VisualTokenCacheEntry:
        """Stores visual KV tensors in cache, running LRU eviction if capacity is exceeded."""
        cache_key = self._generate_cache_key(doc_id, page_number)

        # Evict LRU entries until there is sufficient capacity
        while self.current_token_usage + token_count > self.max_token_capacity and self.cache:
            self._evict_lru_entry()

        entry = VisualTokenCacheEntry(
            cache_key=cache_key,
            doc_id=doc_id,
            page_number=page_number,
            token_count=token_count,
            kv_tensor_ref=kv_tensor_ref
        )
        
        self.cache[cache_key] = entry
        self.current_token_usage += token_count
        return entry

    def _evict_lru_entry(self) -> None:
        """Evicts the least recently accessed visual cache entry."""
        if not self.cache:
            return

        lru_key = min(self.cache.keys(), key=lambda k: self.cache[k].last_accessed_at)
        evicted = self.cache.pop(lru_key)
        self.current_token_usage -= evicted.token_count