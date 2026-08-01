import math
from typing import List, Dict, Any, Optional

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculate cosine similarity between two vector embeddings."""
    if len(v1) != len(v2):
        raise ValueError("Vectors must be of the same dimension.")
    
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude_v1 = math.sqrt(sum(a * a for a in v1))
    magnitude_v2 = math.sqrt(sum(b * b for b in v2))
    
    if magnitude_v1 == 0 or magnitude_v2 == 0:
        return 0.0
        
    return dot_product / (magnitude_v1 * magnitude_v2)

class VectorStore:
    """In-memory vector store for managing document chunks and metadata."""
    def __init__(self):
        self.documents: List[Dict[str, Any]] = []

    def add_document(self, doc_id: str, text: str, embedding: List[float], metadata: Optional[Dict[str, Any]] = None):
        """Add a document chunk with its vector embedding."""
        self.documents.append({
            "id": doc_id,
            "text": text,
            "embedding": embedding,
            "metadata": metadata or {}
        })

    def search(self, query_embedding: List[float], top_k: int = 2) -> List[Dict[str, Any]]:
        """Retrieve top-K most similar documents ranked by cosine similarity."""
        scored_docs = []
        for doc in self.documents:
            score = cosine_similarity(query_embedding, doc["embedding"])
            scored_docs.append({**doc, "score": score})
        
        # Sort descending by similarity score
        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        return scored_docs[:top_k]