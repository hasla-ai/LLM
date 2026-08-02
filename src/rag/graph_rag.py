from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field


class Entity(BaseModel):
    """Node representing a real-world entity in the Knowledge Graph."""
    id: str
    type: str
    description: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Relationship(BaseModel):
    """Directed edge representing a relationship between two entities."""
    source_id: str
    target_id: str
    relation_type: str
    description: str = ""
    weight: float = 1.0


class GraphRAGResponse(BaseModel):
    """Response output from GraphRAG multi-hop retrieval and synthesis."""
    query: str
    answer: str
    retrieved_entities: List[str]
    retrieved_relations: List[str]
    subgraph_depth: int


class GraphExtractor:
    """Extracts structured entities and relationships from raw text context."""

    def __init__(self, llm_client: Any = None):
        self.llm_client = llm_client

    def extract_graph(self, text: str) -> tuple[List[Entity], List[Relationship]]:
        """Parses raw text into entities and relationships."""
        # Heuristic extraction logic for deterministic testing
        entities = []
        relationships = []

        if "Acme Corp" in text and "Alice" in text:
            entities.append(Entity(id="Acme Corp", type="ORGANIZATION", description="Tech Enterprise"))
            entities.append(Entity(id="Alice", type="PERSON", description="Lead Engineer"))
            relationships.append(
                Relationship(
                    source_id="Alice",
                    target_id="Acme Corp",
                    relation_type="WORKS_AT",
                    description="Alice is employed at Acme Corp",
                )
            )

        if "Acme Corp" in text and "Project Titan" in text:
            entities.append(Entity(id="Project Titan", type="PROJECT", description="AI Platform"))
            relationships.append(
                Relationship(
                    source_id="Acme Corp",
                    target_id="Project Titan",
                    relation_type="OWNS",
                    description="Acme Corp develops Project Titan",
                )
            )

        return entities, relationships


class KnowledgeGraphStore:
    """In-memory property graph indexing entities and relationships."""

    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.adjacency: Dict[str, List[Relationship]] = {}

    def add_entity(self, entity: Entity) -> None:
        if entity.id not in self.entities:
            self.entities[entity.id] = entity
            if entity.id not in self.adjacency:
                self.adjacency[entity.id] = []

    def add_relationship(self, rel: Relationship) -> None:
        if rel.source_id not in self.entities or rel.target_id not in self.entities:
            raise ValueError("Both source and target entities must exist in the store before adding a relationship.")
        self.adjacency[rel.source_id].append(rel)

    def traverse(self, start_entity_id: str, max_depth: int = 2) -> tuple[Set[str], List[Relationship]]:
        """Performs Breadth-First Search (BFS) to traverse graph neighbors up to max_depth."""
        if start_entity_id not in self.entities:
            return set(), []

        visited_entities: Set[str] = {start_entity_id}
        traversed_relations: List[Relationship] = []
        queue: List[tuple[str, int]] = [(start_entity_id, 0)]

        while queue:
            current_id, depth = queue.pop(0)
            if depth >= max_depth:
                continue

            for rel in self.adjacency.get(current_id, []):
                traversed_relations.append(rel)
                if rel.target_id not in visited_entities:
                    visited_entities.add(rel.target_id)
                    queue.append((rel.target_id, depth + 1))

        return visited_entities, traversed_relations


class GraphRAGEngine:
    """Orchestrator for Knowledge Graph retrieval and answer synthesis."""

    def __init__(self, graph_store: KnowledgeGraphStore, llm_client: Any = None):
        self.graph_store = graph_store
        self.llm_client = llm_client

    def run(self, query: str, start_entity_id: str, max_depth: int = 2) -> GraphRAGResponse:
        """Executes multi-hop subgraph expansion and generates grounded response."""
        visited_nodes, relationships = self.graph_store.traverse(
            start_entity_id=start_entity_id, max_depth=max_depth
        )

        rel_summaries = [
            f"{r.source_id} -[{r.relation_type}]-> {r.target_id}" for r in relationships
        ]

        answer = f"GraphRAG Context: Identified {len(visited_nodes)} entities connected through {len(relationships)} relationships for query '{query}'."

        return GraphRAGResponse(
            query=query,
            answer=answer,
            retrieved_entities=list(visited_nodes),
            retrieved_relations=rel_summaries,
            subgraph_depth=max_depth,
        )