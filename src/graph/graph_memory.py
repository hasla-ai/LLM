import uuid
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class EntityNode(BaseModel):
    """Represents a unique entity in the Knowledge Graph."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    entity_type: str  # e.g., "Person", "Technology", "Organization", "Concept"
    properties: Dict[str, str] = Field(default_factory=dict)


class RelationEdge(BaseModel):
    """Represents a directed relationship between two Entity Nodes."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str
    target_id: str
    relation_type: str  # e.g., "DEPENDS_ON", "CREATED_BY", "USES"
    weight: float = 1.0


class GraphTraversalResult(BaseModel):
    """Container for multi-hop graph search results."""
    subgraph_nodes: List[EntityNode]
    subgraph_edges: List[RelationEdge]
    fact_triples: List[Tuple[str, str, str]]  # (Source Name, Relation, Target Name)


class KnowledgeGraphMemoryEngine:
    """
    Multi-Hop Knowledge Graph Memory Engine for GraphRAG retrieval.
    Stores domain entities and relations, supporting multi-hop graph traversal.
    """

    def __init__(self):
        self.nodes: Dict[str, EntityNode] = {}
        self.edges: Dict[str, RelationEdge] = {}
        # Name-to-ID lookup index
        self._name_index: Dict[str, str] = {}

    def add_entity(self, name: str, entity_type: str, properties: Optional[Dict[str, str]] = None) -> EntityNode:
        """Add or update an entity node in the graph."""
        clean_name = name.strip()
        if clean_name.lower() in self._name_index:
            node_id = self._name_index[clean_name.lower()]
            node = self.nodes[node_id]
            if properties:
                node.properties.update(properties)
            return node

        node = EntityNode(name=clean_name, entity_type=entity_type, properties=properties or {})
        self.nodes[node.id] = node
        self._name_index[clean_name.lower()] = node.id
        return node

    def add_relation(self, source_entity: str, relation_type: str, target_entity: str, weight: float = 1.0) -> RelationEdge:
        """Create a directed relationship triple (Source) -[Relation]-> (Target)."""
        source_node = self.add_entity(source_entity, entity_type="Concept")
        target_node = self.add_entity(target_entity, entity_type="Concept")

        edge = RelationEdge(
            source_id=source_node.id,
            target_id=target_node.id,
            relation_type=relation_type.upper(),
            weight=weight
        )
        self.edges[edge.id] = edge
        return edge

    def traverse_subgraph(self, start_entity_name: str, max_hops: int = 2) -> GraphTraversalResult:
        """Perform BFS multi-hop traversal to extract contextual subgraph and facts."""
        clean_name = start_entity_name.strip().lower()
        if clean_name not in self._name_index:
            return GraphTraversalResult(subgraph_nodes=[], subgraph_edges=[], fact_triples=[])

        start_node_id = self._name_index[clean_name]
        visited_nodes: Dict[str, EntityNode] = {start_node_id: self.nodes[start_node_id]}
        visited_edges: Dict[str, RelationEdge] = {}
        fact_triples: List[Tuple[str, str, str]] = []

        current_frontier = {start_node_id}

        for _ in range(max_hops):
            next_frontier = set()
            for current_id in current_frontier:
                # Find outgoing and incoming edges
                for edge in self.edges.values():
                    neighbor_id = None
                    if edge.source_id == current_id:
                        neighbor_id = edge.target_id
                    elif edge.target_id == current_id:
                        neighbor_id = edge.source_id

                    if neighbor_id and edge.id not in visited_edges:
                        visited_edges[edge.id] = edge
                        source_name = self.nodes[edge.source_id].name
                        target_name = self.nodes[edge.target_id].name
                        fact_triples.append((source_name, edge.relation_type, target_name))

                        if neighbor_id not in visited_nodes:
                            visited_nodes[neighbor_id] = self.nodes[neighbor_id]
                            next_frontier.add(neighbor_id)

            current_frontier = next_frontier
            if not current_frontier:
                break

        return GraphTraversalResult(
            subgraph_nodes=list(visited_nodes.values()),
            subgraph_edges=list(visited_edges.values()),
            fact_triples=fact_triples
        )