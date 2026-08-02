import pytest
from src.rag.graph_rag import (
    Entity,
    GraphExtractor,
    GraphRAGEngine,
    KnowledgeGraphStore,
    Relationship,
)


@pytest.fixture
def populated_graph_store():
    store = KnowledgeGraphStore()
    e1 = Entity(id="Alice", type="PERSON")
    e2 = Entity(id="Acme Corp", type="ORGANIZATION")
    e3 = Entity(id="Project Titan", type="PROJECT")

    store.add_entity(e1)
    store.add_entity(e2)
    store.add_entity(e3)

    store.add_relationship(
        Relationship(source_id="Alice", target_id="Acme Corp", relation_type="WORKS_AT")
    )
    store.add_relationship(
        Relationship(source_id="Acme Corp", target_id="Project Titan", relation_type="OWNS")
    )

    return store


def test_graph_extractor():
    extractor = GraphExtractor()
    text = "Alice works at Acme Corp on Project Titan."
    entities, rels = extractor.extract_graph(text)

    assert len(entities) == 3
    assert len(rels) == 2
    assert any(e.id == "Alice" for e in entities)


def test_knowledge_graph_store_traversal(populated_graph_store):
    visited, rels = populated_graph_store.traverse(start_entity_id="Alice", max_depth=2)

    assert "Alice" in visited
    assert "Acme Corp" in visited
    assert "Project Titan" in visited
    assert len(rels) == 2


def test_graph_rag_engine_execution(populated_graph_store):
    engine = GraphRAGEngine(graph_store=populated_graph_store)
    response = engine.run(
        query="What projects is Alice associated with?",
        start_entity_id="Alice",
        max_depth=2,
    )

    assert response.query == "What projects is Alice associated with?"
    assert "Alice" in response.retrieved_entities
    assert "Project Titan" in response.retrieved_entities
    assert response.subgraph_depth == 2


def test_invalid_relationship_addition():
    store = KnowledgeGraphStore()
    store.add_entity(Entity(id="Alice", type="PERSON"))

    rel = Relationship(source_id="Alice", target_id="NonExistent", relation_type="KNOWS")
    with pytest.raises(ValueError, match="Both source and target entities must exist"):
        store.add_relationship(rel)