import unittest
from src.core.semantic_cache import SemanticCacheEngine


class TestSemanticCacheEngine(unittest.TestCase):
    def setUp(self):
        self.cache = SemanticCacheEngine(similarity_threshold=0.85)

        # Populate cache with a reference item
        # Dummy 4D embedding for "How do I reset my password?"
        self.ref_embedding = [0.8, 0.2, 0.1, 0.5]
        self.cache.set(
            cache_id="c_01",
            query_text="How do I reset my password?",
            embedding=self.ref_embedding,
            response_text="Go to Settings > Account > Reset Password.",
            model_id="gpt-4o",
            tenant_id="tenant_alpha"
        )

    def test_exact_semantic_cache_hit(self):
        # Searching with exact same embedding
        result = self.cache.get(query_embedding=self.ref_embedding, tenant_id="tenant_alpha")

        self.assertTrue(result.is_hit)
        self.assertEqual(result.similarity_score, 1.0)
        self.assertEqual(result.cached_response, "Go to Settings > Account > Reset Password.")

    def test_similar_semantic_cache_hit(self):
        # Slightly shifted vector simulating semantically similar query
        similar_embedding = [0.79, 0.21, 0.10, 0.49]
        result = self.cache.get(query_embedding=similar_embedding, tenant_id="tenant_alpha")

        self.assertTrue(result.is_hit)
        self.assertGreaterEqual(result.similarity_score, 0.85)

    def test_semantic_cache_miss_on_dissimilar_query(self):
        # Vector pointing in different direction ("What is company revenue?")
        different_embedding = [-0.1, 0.9, 0.8, -0.2]
        result = self.cache.get(query_embedding=different_embedding, tenant_id="tenant_alpha")

        self.assertFalse(result.is_hit)
        self.assertIsNone(result.cached_response)

    def test_tenant_isolation_in_cache(self):
        # Different tenant querying same embedding should miss if restricted
        result = self.cache.get(query_embedding=self.ref_embedding, tenant_id="tenant_beta")
        self.assertFalse(result.is_hit)


if __name__ == "__main__":
    unittest.main()