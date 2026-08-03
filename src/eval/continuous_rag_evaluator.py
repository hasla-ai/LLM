from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class RAGEvalMetrics(BaseModel):
    """Payload representing computed RAG quality and faithfulness scores."""
    eval_id: str
    faithfulness_score: float = Field(ge=0.0, le=1.0)
    answer_relevance_score: float = Field(ge=0.0, le=1.0)
    context_recall_score: float = Field(ge=0.0, le=1.0)
    overall_quality_score: float = Field(ge=0.0, le=1.0)
    is_hallucination_suspected: bool = False


class ContinuousRAGEvaluatorEngine:
    """
    Mission 42: Continuous Automated RAG Evaluation & Hallucination Benchmark Harness.
    Asynchronously evaluates RAG prompt/response pairs against retrieved context chunks.
    """

    def __init__(self, hallucination_threshold: float = 0.60):
        self.hallucination_threshold = hallucination_threshold

    def evaluate_rag_triplet(
        self,
        eval_id: str,
        query: str,
        retrieved_contexts: List[str],
        generated_answer: str
    ) -> RAGEvalMetrics:
        """
        Evaluates a RAG triplet (Query, Retrieved Context, Generated Answer)
        for faithfulness, relevance, and recall.
        """
        faithfulness = self._compute_faithfulness(generated_answer, retrieved_contexts)
        relevance = self._compute_answer_relevance(query, generated_answer)
        recall = self._compute_context_recall(query, retrieved_contexts)

        overall = round((faithfulness + relevance + recall) / 3.0, 4)
        is_hallucinated = faithfulness < self.hallucination_threshold

        return RAGEvalMetrics(
            eval_id=eval_id,
            faithfulness_score=round(faithfulness, 4),
            answer_relevance_score=round(relevance, 4),
            context_recall_score=round(recall, 4),
            overall_quality_score=overall,
            is_hallucination_suspected=is_hallucinated
        )

    def _compute_faithfulness(self, answer: str, contexts: List[str]) -> float:
        """Heuristic check verifying answer token overlap against retrieved context."""
        if not contexts or not answer:
            return 0.0

        combined_context = " ".join(contexts).lower()
        answer_words = set(answer.lower().split())

        if not answer_words:
            return 0.0

        overlap = sum(1 for word in answer_words if word in combined_context)
        return min(overlap / len(answer_words), 1.0)

    def _compute_answer_relevance(self, query: str, answer: str) -> float:
        """Heuristic evaluation measuring query term alignment with the generated answer."""
        if not query or not answer:
            return 0.0

        query_words = set(query.lower().split())
        answer_words = set(answer.lower().split())

        if not query_words:
            return 0.0

        shared = query_words.intersection(answer_words)
        return len(shared) / len(query_words)

    def _compute_context_recall(self, query: str, contexts: List[str]) -> float:
        """Measures whether retrieved context chunks contain key query concepts."""
        if not query or not contexts:
            return 0.0

        combined_context = " ".join(contexts).lower()
        query_words = set(query.lower().split())

        if not query_words:
            return 0.0

        found = sum(1 for word in query_words if word in combined_context)
        return min(found / len(query_words), 1.0)