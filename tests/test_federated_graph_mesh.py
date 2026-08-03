import unittest
from src.graph.federated_graph_mesh import (
    FederatedKnowledgeGraphMesh,
    GraphEntity,
    GraphRelation,
)


class TestFederatedKnowledgeGraphMesh(unittest.TestCase):
    def setUp(self):
        self.mesh = FederatedKnowledgeGraphMesh()

        # Nodes across namespaces
        e1 = GraphEntity(entity_id="usr_1", name="Alice", category="User", namespace="iam")
        e2 = GraphEntity(entity_id="proj_101", name="AlphaProject", category="Project", namespace="engineering")
        e3 = GraphEntity(entity_id="doc_202", name="SecurityCompliancePDF", category="Document", namespace="legal")

        self.mesh.add_entity(e1)
        self.mesh.add_entity(e2)
        self.mesh.add_entity(e3)

        # Edges
        self.mesh.add_relation(GraphRelation(source_id="usr_1", target_id="proj_101", relation_type="OWNS"))
        self.mesh.add_relation(GraphRelation(source_id="proj_101", target_id="doc_202", relation_type="GOVERNED_BY"))

    def test_multi_hop_subgraph_traversal(self):
        # 2-hop search from 'usr_1' should reach both 'proj_101' and 'doc_202'
        result = self.mesh.extract_entity_subgraph(seed_entity_ids=["usr_1"], max_hops=2)

        self.assertEqual(len(result.entities), 3)
        self.assertEqual(len(result.relations), 2)
        self.assertIn("iam", result.explored_namespaces)
        self.assertIn("engineering", result.explored_namespaces)
        self.assertIn("legal", result.explored_namespaces)

    def test_single_hop_containment(self):
        # 1-hop search from 'usr_1' should only reach 'proj_101'
        result = self.mesh.extract_entity_subgraph(seed_entity_ids=["usr_1"], max_hops=1)

        self.assertEqual(len(result.entities), 2)
        self.assertNotIn("legal", result.explored_namespaces)


if __name__ == "__main__":
    unittest.main()