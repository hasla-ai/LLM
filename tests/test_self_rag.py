from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from src.core.llm_client import StructuredLLMClient
from src.rag.vector_store import VectorStore


class RetrieveDecision(str, Enum):
    YES = "YES"
    NO = "NO"


class RelevanceGrade(str, Enum):
    RELEVANT = "RELEVANT"
    IRRELEVANT = "IRRELEVANT"


class SupportGrade(str, Enum):
    FULLY_SUPPORTED = "FULLY_SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"


class UtilityGrade(int, Enum):
    POOR = 1
    FAIR = 3
    EXCELLENT = 5


class ReflectionEvaluation(BaseModel):
    """Container for Self-RAG reflection token grades."""
    retrieve: RetrieveDecision = Field(..., description="[Retrieve]: Is retrieval required for this prompt?")
    is_relevant: RelevanceGrade = Field(..., description="[IsREL]: Is retrieved passage relevant?")
    is_supported: SupportGrade = Field(..., description="[IsSUP]: Is generated candidate supported by context?")
    is_useful: UtilityGrade = Field(..., description="[IsUSE]: Overall response utility score (1-5).")
    reasoning: str = Field(..., description="Explanation for reflection grades.")


class SelfRAGResponse(BaseModel):
    """Final output from the Self-RAG Pipeline."""
    query: str
    was_retrieval_needed: bool
    reflection: ReflectionEvaluation
    final_answer: str
    sources: List[str]


class SelfRAGEngine:
    """Self-Reflective RAG Engine with dynamic reflection tokens and interleaved self-correction."""

    REFLECTION_SYSTEM_PROMPT = """
You are a Self-RAG reflection critic. Evaluate the interaction using reflection metrics:
1. Retrieve: Decide if external knowledge retrieval is necessary ('YES') or if direct response is sufficient ('NO').
2. IsREL: Grade if retrieved context is RELEVANT or IRRELEVANT to the query.
3. IsSUP: Grade if candidate text is FULLY_SUPPORTED, PARTIALLY_SUPPORTED, or UNSUPPORTED by context.
4. IsUSE: Rate overall answer utility from 1 (POOR) to 5 (EXCELLENT).
"""

    SYNTHESIS_SYSTEM_PROMPT = """
Answer the user prompt accurately. Use provided context if available, ensuring every fact is strictly supported.
"""

    def __init__(self, llm_client: StructuredLLMClient, vector_store: VectorStore):
        self.llm_client = llm_client
        self.vector_store = vector_store

    def _evaluate_reflection(self, query: str, context: str, candidate_answer: str) -> ReflectionEvaluation:
        prompt = (
            f"Query: {query}\n\n"
            f"Retrieved Context: {context}\n\n"
            f"Candidate Answer: {candidate_answer}"
        )
        return self.llm_client.generate(
            prompt=prompt,
            response_schema=ReflectionEvaluation,
            system_prompt=self.REFLECTION_SYSTEM_PROMPT
        )

    def run(self, query: str, top_k: int = 2) -> SelfRAGResponse:
        """Full Self-RAG Loop: Decide Retrieval -> Retrieve & Candidate Generation -> Reflect & Filter -> Output."""
        # 1. Decide if retrieval is required via pre-check
        class InitialRetrieveCheck(BaseModel):
            needs_retrieval: bool
            reason: str

        pre_check = self.llm_client.generate(
            prompt=f"Does answering this query require external factual retrieval? Query: {query}",
            response_schema=InitialRetrieveCheck
        )

        sources = []
        context_str = ""

        if pre_check.needs_retrieval:
            # 2. Retrieve Documents
            docs = self.vector_store.search(query, top_k=top_k)
            context_str = "\n".join([d["content"] for d in docs])
            sources = [d.get("id", f"doc_{i}") for i, d in enumerate(docs)]

        # 3. Candidate Answer Generation
        class CandidateAnswer(BaseModel):
            answer: str

        gen_prompt = f"Query: {query}\nContext: {context_str}" if context_str else f"Query: {query}"
        candidate = self.llm_client.generate(
            prompt=gen_prompt,
            response_schema=CandidateAnswer,
            system_prompt=self.SYNTHESIS_SYSTEM_PROMPT
        )

        # 4. Reflection Step ([IsREL], [IsSUP], [IsUSE])
        reflection = self._evaluate_reflection(query, context_str or "N/A", candidate.answer)

        # 5. Self-Correction Fallback if unsupported/hallucinated
        final_answer = candidate.answer
        if context_str and reflection.is_supported == SupportGrade.UNSUPPORTED:
            # Strict fallback generation restricting to context
            class GroundedAnswer(BaseModel):
                strictly_grounded_answer: str

            grounded = self.llm_client.generate(
                prompt=f"STRICT INSTRUCTION: Output ONLY facts directly present in this context: {context_str}\nQuery: {query}",
                response_schema=GroundedAnswer
            )
            final_answer = grounded.strictly_grounded_answer

        return SelfRAGResponse(
            query=query,
            was_retrieval_needed=pre_check.needs_retrieval,
            reflection=reflection,
            final_answer=final_answer,
            sources=sources if pre_check.needs_retrieval else []
        )