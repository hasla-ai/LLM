from typing import List
from pydantic import BaseModel, Field
from src.core.llm_client import StructuredLLMClient
from src.rag.vector_store import VectorStore

class RAGResponse(BaseModel):
    """Structured response output for RAG synthesis."""
    answer: str = Field(description="Synthesized answer based strictly on retrieved context")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0", ge=0.0, le=1.0)
    sources_used: List[str] = Field(description="List of document IDs used as source context")

class RAGPipeline:
    """Orchestrates document retrieval and structured LLM response generation."""
    def __init__(self, llm_client: StructuredLLMClient, vector_store: VectorStore):
        self.llm_client = llm_client
        self.vector_store = vector_store

    def query(self, user_query: str, query_embedding: List[float], top_k: int = 2) -> RAGResponse:
        """Retrieve context and synthesize structured answer."""
        retrieved_docs = self.vector_store.search(query_embedding, top_k=top_k)
        
        # Format context for prompt injection
        context_blocks = [
            f"[Source ID: {doc['id']}]\n{doc['text']}" 
            for doc in retrieved_docs
        ]
        context_str = "\n\n".join(context_blocks)
        
        prompt = (
            f"Context:\n{context_str}\n\n"
            f"Question: {user_query}\n\n"
            "Answer the question accurately based ONLY on the provided context."
        )

        return self.llm_client.generate_structured(prompt, RAGResponse)