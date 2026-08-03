from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field


class GraphEntity(BaseModel):
    """Represents a node entity within a knowledge graph namespace."""
    entity_id: str
    name: str
    category: str
    namespace: str
    attributes: Dict[str, str] = Field(default_factory=dict)


class GraphRelation(BaseModel):
    """Represents a directed relationship edge between two entities."""
    source_id: str
    target_id: str
    relation_type: str
    weight: float = 1.0


class SubgraphQueryResult(BaseModel):
    """Extracted subgraph payload for GraphRAG prompt context augmentation."""
    entities: List[GraphEntity]
    relations: List[GraphRelation]
    explored_namespaces: List[str]


class FederatedKnowledgeGraphMesh:
    """
    Mission 40: Enterprise Federated Knowledge Graph & GraphRAG Entity Linking Mesh.
    Manages multi-namespace entity linking and federated multi-hop relationship traversal.
    """

    def __init__(self):
        self._entities: Dict[str, GraphEntity] = {}
        self._relations: List[GraphRelation] = []

    def add_entity(self, entity: GraphEntity):
        """Registers a entity node into the federated graph topology."""
        self._entities[entity.entity_id] = entity

    def add_relation(self, relation: GraphRelation):
        """Registers a relationship edge connecting two entities."""
        self._relations.append(relation)

    def extract_entity_subgraph(
            self,
            seed_entity_ids: List[str],
            max_hops: int = 2
        ) -> SubgraphQueryResult:
            """
            Executes a multi-hop BFS graph walk starting from seed entities to assemble
            a contextual subgraph spanning federated namespaces.
            """
            visited_entity_ids: Set[str] = set(seed_entity_ids)
            current_frontier: Set[str] = set(seed_entity_ids)
            collected_relations: List[GraphRelation] = []
            seen_relation_keys: Set[tuple] = set()

            for _ in range(max_hops):
                next_frontier: Set[str] = set()
                for rel in self._relations:
                    rel_key = (rel.source_id, rel.target_id, rel.relation_type)
                    
                    if rel.source_id in current_frontier:
                        if rel_key not in seen_relation_keys:
                            seen_relation_keys.add(rel_key)
                            collected_relations.append(rel)
                        if rel.target_id not in visited_entity_ids:
                            visited_entity_ids.add(rel.target_id)
                            next_frontier.add(rel.target_id)
                    elif rel.target_id in current_frontier:
                        if rel_key not in seen_relation_keys:
                            seen_relation_keys.add(rel_key)
                            collected_relations.append(rel)
                        if rel.source_id not in visited_entity_ids:
                            visited_entity_ids.add(rel.source_id)
                            next_frontier.add(rel.source_id)
                current_frontier = next_frontier

            collected_entities = [
                self._entities[e_id] for e_id in visited_entity_ids if e_id in self._entities
            ]
            namespaces = list({e.namespace for e in collected_entities})

            return SubgraphQueryResult(
                entities=collected_entities,
                relations=collected_relations,
                explored_namespaces=namespaces
            )