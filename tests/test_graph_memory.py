import unittest
from src.graph.graph_memory import KnowledgeGraphMemoryEngine
class TestKnowledgeGraphMemoryEngine(unittest.TestCase):
    def setUp(self):
        self.engine = KnowledgeGraphMemoryEngine()
        
        # Build test knowledge graph
        self.engine.add_relation("Persistent Memory", "USES", "RRF Fusion")
        self.engine.add_relation("RRF Fusion", "DEPENDS_ON", "BM25 Search")
        self.engine.add_relation("RRF Fusion", "DEPENDS_ON", "Cosine Similarity")
        self.engine.add_relation("Agent Kernel OS", "IMPLEMENTS", "Persistent Memory")

    def test_add_entity_and_deduplication(self):
        node1 = self.engine.add_entity("LangChain", "Organization")
        node2 = self.engine.add_entity("langchain", "Organization")  # Case insensitive duplicate
        
        self.assertEqual(node1.id, node2.id)

    def test_add_relation(self):
        edge = self.engine.add_relation("GraphRAG", "EXTENDS", "RAG")
        self.assertEqual(edge.relation_type, "EXTENDS")
        self.assertIn("graphrag", self.engine._name_index)

    def test_multi_hop_traversal(self):
        # 1-hop traversal from "Agent Kernel OS"
        result_1hop = self.engine.traverse_subgraph("Agent Kernel OS", max_hops=1)
        self.assertEqual(len(result_1hop.subgraph_nodes), 2)  # Agent Kernel OS, Persistent Memory
        
        # 2-hop traversal from "Agent Kernel OS" -> Persistent Memory -> RRF Fusion
        result_2hop = self.engine.traverse_subgraph("Agent Kernel OS", max_hops=2)
        self.assertGreaterEqual(len(result_2hop.subgraph_nodes), 3)
        
        # Check extracted fact triple
        facts = result_2hop.fact_triples
        self.assertIn(("Agent Kernel OS", "IMPLEMENTS", "Persistent Memory"), facts)
        self.assertIn(("Persistent Memory", "USES", "RRF Fusion"), facts)


if __name__ == "__main__":
    unittest.main()