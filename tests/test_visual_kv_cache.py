import unittest
import time
from src.core.visual_kv_cache import VisualKVCacheEngine


class TestVisualKVCacheEngine(unittest.TestCase):
    def setUp(self):
        # Small capacity for deterministic eviction testing (capacity = 2000 tokens)
        self.cache_engine = VisualKVCacheEngine(max_token_capacity=2000)

    def test_store_and_retrieve_visual_tokens(self):
        entry = self.cache_engine.store_visual_tokens(
            doc_id="blueprint_doc_01",
            page_number=1,
            token_count=1024,
            kv_tensor_ref="gpu_ptr_0x7f01"
        )
        self.assertEqual(entry.cache_key, "blueprint_doc_01_p1")
        self.assertEqual(self.cache_engine.current_token_usage, 1024)

        retrieved = self.cache_engine.get_visual_tokens("blueprint_doc_01", 1)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.access_count, 2)

    def test_lru_eviction_policy(self):
        # Store Page 1 (1000 tokens)
        self.cache_engine.store_visual_tokens("doc_a", 1, 1000, "ptr_a1")
        time.sleep(0.01)

        # Store Page 2 (1000 tokens)
        self.cache_engine.store_visual_tokens("doc_a", 2, 1000, "ptr_a2")
        time.sleep(0.01)

        # Access Page 1 again so Page 2 becomes the LRU
        self.cache_engine.get_visual_tokens("doc_a", 1)
        time.sleep(0.01)

        # Store Page 3 (500 tokens) -> Requires evicting Page 2
        self.cache_engine.store_visual_tokens("doc_a", 3, 500, "ptr_a3")

        # Verify Page 2 was evicted while Page 1 and Page 3 remain
        self.assertIsNone(self.cache_engine.get_visual_tokens("doc_a", 2))
        self.assertIsNotNone(self.cache_engine.get_visual_tokens("doc_a", 1))
        self.assertIsNotNone(self.cache_engine.get_visual_tokens("doc_a", 3))


if __name__ == "__main__":
    unittest.main()