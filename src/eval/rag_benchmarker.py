import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.core.llm_client import StructuredLLMClient


class MetricScore(BaseModel):
    """Pydantic model for an individual evaluation metric score."""
    metric_name: str = Field(..., description="Name of the metric evaluated (e.g., faithfulness, relevance).")
    score: float = Field(..., description="Normalized score from 0.0 (worst) to 1.0 (best).")
    reasoning: str = Field(..., description="Detailed explanation for the assigned score.")


class RAGEvaluationResult(BaseModel):
    """Evaluation result for a single query execution."""
    query: str
    answer: str
    retrieved_contexts: List[str]
    latency_seconds: float
    faithfulness: MetricScore
    answer_relevance: MetricScore
    context_precision: MetricScore


class StrategyBenchmarkSummary(BaseModel):
    """Aggregated benchmark metrics for a specific RAG strategy."""
    strategy_name: str
    total_queries: int
    avg_faithfulness: float
    avg_answer_relevance: float
    avg_context_precision: float
    avg_latency_seconds: float


class RAGBenchmarkReport(BaseModel):
    """Comprehensive evaluation report across evaluated strategies."""
    summaries: List[StrategyBenchmarkSummary]
    detailed_results: List[RAGEvaluationResult]


class RAGBenchmarker:
    """Enterprise RAG Evaluation engine performing LLM-as-a-Judge quality scoring."""

    EVAL_FAITHFULNESS_PROMPT = """
You are an expert factual evaluator. Analyze whether the generated answer is strictly grounded in the provided context passages.
Assign a score from 0.0 to 1.0:
- 1.0: Every claim in the answer is completely supported by the context (no hallucinations).
- 0.5: Partial support, or contains minor unverified extrapolations.
- 0.0: High hallucination rate or direct contradictions to the context.
"""

    EVAL_RELEVANCE_PROMPT = """
You are an expert response auditor. Evaluate whether the generated answer directly addresses the user's query.
Assign a score from 0.0 to 1.0:
- 1.0: Completely answers the user query concisely and directly.
- 0.5: Partially answers the query or contains significant irrelevant tangents.
- 0.0: Completely off-topic or fails to answer the question.
"""

    EVAL_PRECISION_PROMPT = """
You are an expert context auditor. Evaluate whether the retrieved context passages are relevant and necessary to answer the user query.
Assign a score from 0.0 to 1.0:
- 1.0: All retrieved context passages are highly relevant and informative.
- 0.5: Some retrieved passages are relevant, but contain noise/irrelevant text.
- 0.0: None of the retrieved passages are relevant to the query.
"""

    def __init__(self, llm_client: StructuredLLMClient):
        self.llm_client = llm_client

    def evaluate_faithfulness(self, query: str, answer: str, contexts: List[str]) -> MetricScore:
        prompt = f"Query: {query}\n\nContexts:\n" + "\n---\n".join(contexts) + f"\n\nGenerated Answer:\n{answer}"
        result = self.llm_client.generate(
            prompt=prompt,
            response_schema=MetricScore,
            system_prompt=self.EVAL_FAITHFULNESS_PROMPT
        )
        result.metric_name = "faithfulness"
        return result

    def evaluate_answer_relevance(self, query: str, answer: str) -> MetricScore:
        prompt = f"Query: {query}\n\nGenerated Answer:\n{answer}"
        result = self.llm_client.generate(
            prompt=prompt,
            response_schema=MetricScore,
            system_prompt=self.EVAL_RELEVANCE_PROMPT
        )
        result.metric_name = "answer_relevance"
        return result

    def evaluate_context_precision(self, query: str, contexts: List[str]) -> MetricScore:
        prompt = f"Query: {query}\n\nRetrieved Contexts:\n" + "\n---\n".join(contexts)
        result = self.llm_client.generate(
            prompt=prompt,
            response_schema=MetricScore,
            system_prompt=self.EVAL_PRECISION_PROMPT
        )
        result.metric_name = "context_precision"
        return result

    def evaluate_single(
        self,
        query: str,
        answer: str,
        contexts: List[str],
        latency_seconds: float = 0.0
    ) -> RAGEvaluationResult:
        """Runs all three LLM-as-a-Judge metrics for a single RAG response."""
        faithfulness = self.evaluate_faithfulness(query, answer, contexts)
        relevance = self.evaluate_answer_relevance(query, answer)
        precision = self.evaluate_context_precision(query, contexts)

        return RAGEvaluationResult(
            query=query,
            answer=answer,
            retrieved_contexts=contexts,
            latency_seconds=latency_seconds,
            faithfulness=faithfulness,
            answer_relevance=relevance,
            context_precision=precision
        )

    def generate_report(
        self,
        strategy_name: str,
        results: List[RAGEvaluationResult]
    ) -> RAGBenchmarkReport:
        """Aggregates single execution results into a structured benchmark summary report."""
        if not results:
            summary = StrategyBenchmarkSummary(
                strategy_name=strategy_name,
                total_queries=0,
                avg_faithfulness=0.0,
                avg_answer_relevance=0.0,
                avg_context_precision=0.0,
                avg_latency_seconds=0.0
            )
            return RAGBenchmarkReport(summaries=[summary], detailed_results=[])

        total = len(results)
        avg_faith = sum(r.faithfulness.score for r in results) / total
        avg_rel = sum(r.answer_relevance.score for r in results) / total
        avg_prec = sum(r.context_precision.score for r in results) / total
        avg_lat = sum(r.latency_seconds for r in results) / total

        summary = StrategyBenchmarkSummary(
            strategy_name=strategy_name,
            total_queries=total,
            avg_faithfulness=round(avg_faith, 3),
            avg_answer_relevance=round(avg_rel, 3),
            avg_context_precision=round(avg_prec, 3),
            avg_latency_seconds=round(avg_lat, 3)
        )

        return RAGBenchmarkReport(summaries=[summary], detailed_results=results)