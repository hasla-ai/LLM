import math
import unittest
from datetime import datetime, timedelta
from src.rag.persistent_memory import (
    MemoryDocument,
    PersistentMemoryEngine,
    SearchResult,
)


class TestPersistentMemoryEngine(unittest.TestCase):
    def setUp(self):
        self.engine = PersistentMemoryEngine(rrf_k=60)
        now = datetime.now()

        # Document 1: Quantum Machine Learning (Dense target)
        self.doc1 = MemoryDocument(
            id="doc_1",
            content="Quantum machine learning uses variational quantum eigensolvers for optimization.",
            embedding=[0.9, 0.1, 0.0, 0.1],
            created_at=now - timedelta(days=3)
        )

        # Document 2: Agent Middleware & AST Sandbox (Sparse BM25 target)
        self.doc2 = MemoryDocument(
            id="doc_2",
            content="The security sandbox uses AST parsing and token bucket rate limiters.",
            embedding=[0.1, 0.8, 0.2, 0.0],
            created_at=now - timedelta(days=2)
        )

        # Document 3: Persistent Memory & RAG (Hybrid target)
        self.doc3 = MemoryDocument(
            id="doc_3",
            content="Persistent semantic memory stores dense vectors and sparse BM25 keyword indices.",
            embedding=[0.2, 0.2, 0.9, 0.1],
            created_at=now - timedelta(days=1)
        )

        self.engine.add_document(self.doc1)
        self.engine.add_document(self.doc2)
        self.engine.add_document(self.doc3)

    def test_add_and_retrieve_documents(self):
        self.assertEqual(len(self.engine.documents), 3)
        doc = self.engine.documents.get("doc_1")
        self.assertIsNotNone(doc)
        self.assertEqual(doc.id, "doc_1")

    def test_cosine_similarity(self):
        vec_a = [1.0, 0.0, 0.0]
        vec_b = [1.0, 0.0, 0.0]
        vec_c = [0.0, 1.0, 0.0]

        self.assertAlmostEqual(self.engine._cosine_similarity(vec_a, vec_b), 1.0)
        self.assertAlmostEqual(self.engine._cosine_similarity(vec_a, vec_c), 0.0)
        self.assertEqual(self.engine._cosine_similarity([], vec_b), 0.0)

    def test_dense_search(self):
        query_vector = [0.1, 0.1, 0.95, 0.05]
        results = self.engine._dense_search(query_vector, top_k=2)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].document.id, "doc_3")
        self.assertEqual(results[0].rank, 1)

    def test_sparse_bm25_search(self):
        results = self.engine._sparse_bm25_search("sandbox AST", top_k=2)

        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].document.id, "doc_2")
        self.assertEqual(results[0].rank, 1)

    def test_hybrid_search_rrf_fusion(self):
        query_str = "quantum memory BM25"
        query_vector = [0.8, 0.1, 0.1, 0.0]

        results = self.engine.hybrid_search(
            query=query_str, query_vector=query_vector, top_k=3
        )

        self.assertEqual(len(results), 3)
        for idx, res in enumerate(results, start=1):
            self.assertEqual(res.rank, idx)
            self.assertGreater(res.score, 0.0)

    def test_prune_old_memories(self):
        deleted_count = self.engine.prune_old_memories(max_capacity=2)

        self.assertEqual(deleted_count, 1)
        self.assertEqual(len(self.engine.documents), 2)
        self.assertNotIn("doc_1", self.engine.documents)
        self.assertIn("doc_2", self.engine.documents)
        self.assertIn("doc_3", self.engine.documents)


if __name__ == "__main__":
    unittest.main()