from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CachePolicy(str, Enum):
    LRU = "LRU"
    LFU = "LFU"


class ContextChunk(BaseModel):
    """Container for a chunk of text within a long document."""
    chunk_id: str
    content: str
    token_count: int
    start_token_idx: int
    end_token_idx: int
    parent_id: Optional[str] = None


class KVCacheBlock(BaseModel):
    """Simulated KV Cache memory block for a prompt prefix/chunk."""
    block_id: str
    chunk_id: str
    token_count: int
    last_accessed: float
    access_frequency: int = 1


class KVCacheStats(BaseModel):
    """Execution metrics for KV cache performance."""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    evictions: int = 0
    active_blocks: int = 0
    used_tokens: int = 0
    hit_rate: float = 0.0


class HierarchicalChunker:
    """Chunks text based on token limits with configurable overlap."""

    def __init__(self, chunk_size: int = 128, chunk_overlap: int = 16):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be strictly less than chunk_size.")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str, parent_id: Optional[str] = None) -> List[ContextChunk]:
        """Splits raw text into overlapping token chunks."""
        words = text.split()
        if not words:
            return []

        chunks: List[ContextChunk] = []
        step = self.chunk_size - self.chunk_overlap
        current_token_idx = 0

        for i in range(0, len(words), step):
            chunk_words = words[i : i + self.chunk_size]
            chunk_content = " ".join(chunk_words)
            token_count = len(chunk_words)
            end_token_idx = current_token_idx + token_count

            chunk = ContextChunk(
                chunk_id=f"chunk_{len(chunks) + 1}",
                content=chunk_content,
                token_count=token_count,
                start_token_idx=current_token_idx,
                end_token_idx=end_token_idx,
                parent_id=parent_id,
            )
            chunks.append(chunk)
            current_token_idx += step

            if i + self.chunk_size >= len(words):
                break

        return chunks


class DynamicKVCacheManager:
    """Manages allocation, retrieval, and eviction of simulated KV cache blocks."""

    def __init__(
        self,
        max_token_capacity: int = 1024,
        policy: CachePolicy = CachePolicy.LRU,
    ):
        self.max_token_capacity = max_token_capacity
        self.policy = policy
        self.blocks: Dict[str, KVCacheBlock] = {}
        self.access_counter: float = 0.0
        self.total_requests = 0
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    @property
    def used_tokens(self) -> int:
        return sum(b.token_count for b in self.blocks.values())

    def _evict_block(self) -> None:
        """Evicts a single block based on the configured cache policy."""
        if not self.blocks:
            return

        if self.policy == CachePolicy.LRU:
            target_id = min(self.blocks.keys(), key=lambda k: self.blocks[k].last_accessed)
        else:  # LFU
            target_id = min(self.blocks.keys(), key=lambda k: self.blocks[k].access_frequency)

        del self.blocks[target_id]
        self.evictions += 1

    def get_or_allocate(self, chunk: ContextChunk) -> bool:
        """Looks up or allocates a KV cache block for the given chunk. Returns True on cache hit."""
        self.total_requests += 1
        self.access_counter += 1.0

        if chunk.chunk_id in self.blocks:
            self.hits += 1
            block = self.blocks[chunk.chunk_id]
            block.last_accessed = self.access_counter
            block.access_frequency += 1
            return True

        self.misses += 1

        # Evict blocks until space is available
        while self.used_tokens + chunk.token_count > self.max_token_capacity and self.blocks:
            self._evict_block()

        # Allocate new block
        new_block = KVCacheBlock(
            block_id=f"block_{chunk.chunk_id}",
            chunk_id=chunk.chunk_id,
            token_count=chunk.token_count,
            last_accessed=self.access_counter,
            access_frequency=1,
        )
        self.blocks[chunk.chunk_id] = new_block
        return False

    def get_stats(self) -> KVCacheStats:
        """Computes current runtime statistics for the cache."""
        hit_rate = round(self.hits / self.total_requests, 4) if self.total_requests > 0 else 0.0
        return KVCacheStats(
            total_requests=self.total_requests,
            cache_hits=self.hits,
            cache_misses=self.misses,
            evictions=self.evictions,
            active_blocks=len(self.blocks),
            used_tokens=self.used_tokens,
            hit_rate=hit_rate,
        )