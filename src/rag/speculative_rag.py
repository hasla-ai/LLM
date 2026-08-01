from typing import List, Optional
from pydantic import BaseModel, Field
from src.core.llm_client import StructuredLLMClient
from src.rag.vector_store import VectorStore


class DraftAnswer(BaseModel):
    """Candidate draft answer produced by the fast draft model."""
    candidate_text: str = Field(..., description="Draft answer generated from retrieved context.")
    confidence_score: float = Field(..., description="Self-assessed confidence score (0.0 to 1.0).")


class VerificationResult(BaseModel):
    """Structured verification grade from the verifier model."""
    is_accepted: bool = Field(..., description="Whether the draft is factually accurate and complete.")
    verdict_score: float = Field(..., description="Verification score between 0.0 and 1.0.")
    corrected_answer: Optional[str] = Field(None, description="Refined answer if draft was rejected.")
    reasoning: str = Field(..., description="Explanation for acceptance or rejection.")


class SpeculativeRAGResponse(BaseModel):
    """Output payload from the Speculative RAG Pipeline."""
    query: str
    draft_answer: DraftAnswer
    verification: VerificationResult
    final_answer: str
    was_draft_accepted: bool
    sources: List[str]


class SpeculativeRAGPipeline:
    """Speculative RAG Engine combining fast draft generation with verification."""

    DRAFT_SYSTEM_PROMPT = """
You are a fast draft assistant. Based on the provided context, quickly construct a direct candidate answer.
"""

    VERIFIER_SYSTEM_PROMPT = """
You are a rigorous factual verifier. Evaluate the candidate draft answer against the provided context.
If the draft is accurate and complete, set is_accepted=True.
If the draft contains inaccuracies, set is_accepted=False and provide a corrected_answer.
"""

    def __init__(
        self,
        draft_client: StructuredLLMClient,
        verifier_client: StructuredLLMClient,
        vector_store: VectorStore,
        acceptance_threshold: float = 0.8
    ):
        self.draft_client = draft_client
        self.verifier_client = verifier_client
        self.vector_store = vector_store
        self.acceptance_threshold = acceptance_threshold

    def run(self, query: str, top_k: int = 2) -> SpeculativeRAGResponse:
        """Runs the Speculative RAG pipeline: Retrieve -> Draft -> Verify -> Accept or Refine."""
        # 1. Context Retrieval
        retrieved_docs = self.vector_store.search(query, top_k=top_k)
        context_str = "\n".join([doc["content"] for doc in retrieved_docs])
        sources = [doc.get("id", f"doc_{i}") for i, doc in enumerate(retrieved_docs)]

        # 2. Fast Draft Generation
        draft_prompt = f"Context:\n{context_str}\n\nQuery: {query}"
        draft = self.draft_client.generate(
            prompt=draft_prompt,
            response_schema=DraftAnswer,
            system_prompt=self.DRAFT_SYSTEM_PROMPT
        )

        # 3. Verification Step
        verifier_prompt = (
            f"Context:\n{context_str}\n\n"
            f"Query: {query}\n\n"
            f"Candidate Draft:\n{draft.candidate_text}"
        )
        verification = self.verifier_client.generate(
            prompt=verifier_prompt,
            response_schema=VerificationResult,
            system_prompt=self.VERIFIER_SYSTEM_PROMPT
        )

        # 4. Decision Logic: Accept Draft or Use Correction
        accepted = verification.is_accepted and (verification.verdict_score >= self.acceptance_threshold)
        if accepted:
            final_ans = draft.candidate_text
        else:
            final_ans = verification.corrected_answer or draft.candidate_text

        return SpeculativeRAGResponse(
            query=query,
            draft_answer=draft,
            verification=verification,
            final_answer=final_ans,
            was_draft_accepted=accepted,
            sources=sources
        )