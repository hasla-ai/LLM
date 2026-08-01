from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from src.core.llm_client import StructuredLLMClient
from src.rag.vector_store import VectorStore


class RetrievalGrade(str, Enum):
    CORRECT = "CORRECT"
    AMBIGUOUS = "AMBIGUOUS"
    INCORRECT = "INCORRECT"


class EvaluationResult(BaseModel):
    """Grading score assigned to retrieved document chunks."""
    grade: RetrievalGrade = Field(..., description="Classification of retrieval quality relative to the prompt.")
    confidence_score: float = Field(..., description="Score between 0.0 and 1.0 indicating retrieval relevance.")
    reasoning: str = Field(..., description="Explanation for the assigned evaluation grade.")


class CRAGResponse(BaseModel):
    """Final output from the Corrective RAG Pipeline."""
    query: str
    retrieval_grade: RetrievalGrade
    was_web_search_triggered: bool
    refined_context: str
    final_answer: str
    sources: List[str]


class CorrectiveRAGPipeline:
    """Corrective RAG Pipeline with self-correcting document evaluation and search fallback."""

    EVALUATION_SYSTEM_PROMPT = """
You are a strict retrieval evaluator. Assess whether the retrieved document context contains facts directly relevant to answering the user query.
Grade the document as:
- CORRECT: Context contains clear, accurate facts that directly answer the query.
- AMBIGUOUS: Context contains partial hints or noisy information mixed with irrelevant text.
- INCORRECT: Context is irrelevant or fails to address the query.
"""

    SYNTHESIS_SYSTEM_PROMPT = """
You are a precise answer generator. Answer the query using ONLY the provided verified context.
"""

    def __init__(
        self,
        llm_client: StructuredLLMClient,
        vector_store: VectorStore,
        search_tool_func: Optional[callable] = None
    ):
        self.llm_client = llm_client
        self.vector_store = vector_store
        self.search_tool_func = search_tool_func or self._default_mock_search

    def _default_mock_search(self, query: str) -> str:
        """Fallback mock web search handler if no external search tool is injected."""
        return f"[Web Search Result] Up-to-date online information for query: {query}"

    def evaluate_retrieval(self, query: str, context: str) -> EvaluationResult:
        """Grades the quality of retrieved local context."""
        prompt = f"User Query: {query}\n\nRetrieved Context:\n{context}"
        return self.llm_client.generate(
            prompt=prompt,
            response_schema=EvaluationResult,
            system_prompt=self.EVALUATION_SYSTEM_PROMPT
        )

    def run(self, query: str, top_k: int = 2) -> CRAGResponse:
        """Full CRAG Loop: Retrieve -> Grade -> Refine / Fallback Search -> Synthesize."""
        # 1. Local Vector Search
        local_docs = self.vector_store.search(query, top_k=top_k)
        raw_context = "\n".join([doc["content"] for doc in local_docs])
        sources = [doc.get("id", f"doc_{i}") for i, doc in enumerate(local_docs)]

        # 2. Evaluate Local Context Quality
        eval_result = self.evaluate_retrieval(query, raw_context)

        web_search_triggered = False
        final_context = raw_context

        # 3. Action Logic based on Retrieval Grade
        if eval_result.grade == RetrievalGrade.CORRECT:
            # Use high-confidence local context directly
            final_context = raw_context

        elif eval_result.grade == RetrievalGrade.AMBIGUOUS:
            # Trigger web search fallback to augment ambiguous context
            web_search_triggered = True
            web_info = self.search_tool_func(query)
            final_context = f"Local Context:\n{raw_context}\n\nWeb Search Augmentation:\n{web_info}"
            sources.append("web_search_fallback")

        elif eval_result.grade == RetrievalGrade.INCORRECT:
            # Discard local context and rely fully on Web Search fallback
            web_search_triggered = True
            web_info = self.search_tool_func(query)
            final_context = f"Web Search Context:\n{web_info}"
            sources = ["web_search_fallback"]

        # 4. Synthesize Answer
        synthesis_prompt = f"Query: {query}\n\nVerified Context:\n{final_context}"

        class CRAGAnswer(BaseModel):
            answer: str

        synthesis_result = self.llm_client.generate(
            prompt=synthesis_prompt,
            response_schema=CRAGAnswer,
            system_prompt=self.SYNTHESIS_SYSTEM_PROMPT
        )

        return CRAGResponse(
            query=query,
            retrieval_grade=eval_result.grade,
            was_web_search_triggered=web_search_triggered,
            refined_context=final_context,
            final_answer=synthesis_result.answer,
            sources=sources
        )