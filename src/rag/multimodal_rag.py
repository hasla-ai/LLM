import math
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ModalityType(str, Enum):
    TEXT = "text"
    IMAGE = "image"


class MultimodalDocument(BaseModel):
    """Container for multi-modal document chunks (text or visual assets)."""
    doc_id: str
    modality: ModalityType
    content: str = Field(..., description="Text content or Base64/URI representation of image")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None


class MultimodalRAGResponse(BaseModel):
    """Response payload for multi-modal context retrieval and synthesis."""
    query: str
    answer: str
    retrieved_text_sources: List[str]
    retrieved_image_sources: List[str]
    confidence_score: float = Field(..., ge=0.0, le=1.0)


class MultimodalEmbedder:
    """Mock dual-modal embedder projecting text and visual inputs into a shared vector space."""

    def __init__(self, dimension: int = 4):
        self.dimension = dimension

    def embed_text(self, text: str) -> List[float]:
        """Generate a deterministic vector for text inputs."""
        val = sum(ord(c) for c in text) % 100 / 100.0
        return [val, round(1.0 - val, 2), 0.5, 0.25]

    def embed_image(self, image_uri: str) -> List[float]:
        """Generate a deterministic vector for visual assets (diagrams/scans)."""
        val = sum(ord(c) for c in image_uri) % 100 / 100.0
        # Offset to simulate shared latent space alignment
        return [round(val * 0.9, 2), round(1.0 - val, 2), 0.5, 0.25]


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_v1 = math.sqrt(sum(a * a for a in v1))
    norm_v2 = math.sqrt(sum(b * b for b in v2))
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return dot_product / (norm_v1 * norm_v2)


class MultimodalVectorStore:
    """In-memory multi-modal vector index supporting modality-filtered retrieval."""

    def __init__(self):
        self.documents: List[MultimodalDocument] = []

    def add_document(self, doc: MultimodalDocument) -> None:
        if doc.embedding is None:
            raise ValueError(f"Document '{doc.doc_id}' must have an embedding before indexing.")
        self.documents.append(doc)

    def search(
        self,
        query_vector: List[float],
        top_k: int = 3,
        modality_filter: Optional[ModalityType] = None,
    ) -> List[tuple[MultimodalDocument, float]]:
        """Search documents by vector similarity with optional modality filtering."""
        results = []
        for doc in self.documents:
            if modality_filter and doc.modality != modality_filter:
                continue
            sim = cosine_similarity(query_vector, doc.embedding)
            results.append((doc, sim))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]


class MultimodalRAGEngine:
    """Orchestrator combining text and visual search context for multi-modal generation."""

    def __init__(
        self,
        embedder: MultimodalEmbedder,
        vector_store: MultimodalVectorStore,
        llm_client: Any,
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.llm_client = llm_client

    def run(self, query: str, top_k: int = 2) -> MultimodalRAGResponse:
        """Execute multi-modal retrieval and answer synthesis."""
        query_vec = self.embedder.embed_text(query)

        # Retrieve top text and visual contexts
        search_results = self.vector_store.search(query_vec, top_k=top_k * 2)

        text_sources = []
        image_sources = []
        context_snippets = []

        for doc, score in search_results:
            if doc.modality == ModalityType.TEXT:
                text_sources.append(doc.doc_id)
                context_snippets.append(f"[Text Document ({doc.doc_id})]: {doc.content}")
            elif doc.modality == ModalityType.IMAGE:
                image_sources.append(doc.doc_id)
                context_snippets.append(f"[Visual Asset ({doc.doc_id})]: {doc.content}")

        # Synthesize output using mock or structured LLM
        prompt = f"Context:\n" + "\n".join(context_snippets) + f"\n\nQuery: {query}"
        
        # Simulated LLM generation response
        generated_answer = f"Based on the retrieved context and visual diagrams: {query}"

        return MultimodalRAGResponse(
            query=query,
            answer=generated_answer,
            retrieved_text_sources=text_sources[:top_k],
            retrieved_image_sources=image_sources[:top_k],
            confidence_score=0.92,
        )