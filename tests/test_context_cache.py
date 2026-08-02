import pytest
from src.core.context_cache import (
    CachePolicy,
    ContextChunk,
    DynamicKVCacheManager,
    HierarchicalChunker,
)


def test_hierarchical_chunker_basic():
    chunker = HierarchicalChunker(chunk_size=10, chunk_overlap=2)
    text = " ".join([f"word{i}" for i in range(25)])
    chunks = chunker.chunk_text(text)

    assert len(chunks) > 1
    assert chunks[0].token_count == 10
    assert chunks[0].chunk_id == "chunk_1"


def test_hierarchical_chunker_invalid_overlap():
    with pytest.raises(ValueError, match="chunk_overlap must be strictly less than chunk_size"):
        HierarchicalChunker(chunk_size=10, chunk_overlap=10)


def test_kv_cache_hits_and_misses():
    cache_mgr = DynamicKVCacheManager(max_token_capacity=100)
    chunk = ContextChunk(
        chunk_id="c1",
        content="hello world",
        token_count=10,
        start_token_idx=0,
        end_token_idx=10,
    )

    # First access -> Miss
    hit1 = cache_mgr.get_or_allocate(chunk)
    assert hit1 is False

    # Second access -> Hit
    hit2 = cache_mgr.get_or_allocate(chunk)
    assert hit2 is True

    stats = cache_mgr.get_stats()
    assert stats.total_requests == 2
    assert stats.cache_hits == 1
    assert stats.cache_misses == 1
    assert stats.hit_rate == 0.5


def test_kv_cache_lru_eviction():
    cache_mgr = DynamicKVCacheManager(max_token_capacity=20, policy=CachePolicy.LRU)
    chunk1 = ContextChunk(chunk_id="c1", content="one", token_count=10, start_token_idx=0, end_token_idx=10)
    chunk2 = ContextChunk(chunk_id="c2", content="two", token_count=10, start_token_idx=10, end_token_idx=20)
    chunk3 = ContextChunk(chunk_id="c3", content="three", token_count=10, start_token_idx=20, end_token_idx=30)

    cache_mgr.get_or_allocate(chunk1)  # Alloc c1
    cache_mgr.get_or_allocate(chunk2)  # Alloc c2 (Full: 20 tokens)

    # Alloc c3 triggers eviction of LRU block (c1)
    cache_mgr.get_or_allocate(chunk3)

    stats = cache_mgr.get_stats()
    assert stats.evictions == 1
    assert "c1" not in cache_mgr.blocks
    assert "c2" in cache_mgr.blocks
    assert "c3" in cache_mgr.blocks