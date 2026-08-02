from unittest.mock import MagicMock
import pytest
from src.eval.rag_benchmarker import (
    RAGBenchmarker,
    MetricScore,
    RAGEvaluationResult,
    RAGBenchmarkReport
)


def test_evaluator_faithfulness():
    llm_client = MagicMock()
    mock_score = MetricScore(
        metric_name="faithfulness",
        score=1.0,
        reasoning="The answer is fully grounded in the provided context."
    )
    llm_client.generate.return_value = mock_score

    benchmarker = RAGBenchmarker(llm_client=llm_client)
    res = benchmarker.evaluate_faithfulness(
        query="What is X?",
        answer="X is 10.",
        contexts=["X is equal to 10."]
    )

    assert res.score == 1.0
    assert res.metric_name == "faithfulness"
    assert llm_client.generate.called


def test_evaluator_evaluate_single():
    llm_client = MagicMock()

    faith_score = MetricScore(metric_name="faithfulness", score=0.9, reasoning="Good groundings.")
    rel_score = MetricScore(metric_name="answer_relevance", score=1.0, reasoning="Direct answer.")
    prec_score = MetricScore(metric_name="context_precision", score=0.8, reasoning="Relevant contexts.")

    llm_client.generate.side_effect = [faith_score, rel_score, prec_score]

    benchmarker = RAGBenchmarker(llm_client=llm_client)
    eval_result = benchmarker.evaluate_single(
        query="What is the refund window?",
        answer="14 days.",
        contexts=["Refunds are accepted within 14 days."],
        latency_seconds=0.45
    )

    assert isinstance(eval_result, RAGEvaluationResult)
    assert eval_result.faithfulness.score == 0.9
    assert eval_result.answer_relevance.score == 1.0
    assert eval_result.context_precision.score == 0.8
    assert eval_result.latency_seconds == 0.45


def test_generate_benchmark_report():
    llm_client = MagicMock()
    benchmarker = RAGBenchmarker(llm_client=llm_client)

    eval_1 = RAGEvaluationResult(
        query="Q1",
        answer="A1",
        retrieved_contexts=["C1"],
        latency_seconds=0.5,
        faithfulness=MetricScore(metric_name="faithfulness", score=1.0, reasoning="OK"),
        answer_relevance=MetricScore(metric_name="answer_relevance", score=1.0, reasoning="OK"),
        context_precision=MetricScore(metric_name="context_precision", score=0.8, reasoning="OK")
    )
    eval_2 = RAGEvaluationResult(
        query="Q2",
        answer="A2",
        retrieved_contexts=["C2"],
        latency_seconds=0.3,
        faithfulness=MetricScore(metric_name="faithfulness", score=0.8, reasoning="OK"),
        answer_relevance=MetricScore(metric_name="answer_relevance", score=0.8, reasoning="OK"),
        context_precision=MetricScore(metric_name="context_precision", score=0.6, reasoning="OK")
    )

    report = benchmarker.generate_report("Adaptive RAG", [eval_1, eval_2])

    assert isinstance(report, RAGBenchmarkReport)
    assert len(report.summaries) == 1
    summary = report.summaries[0]
    assert summary.strategy_name == "Adaptive RAG"
    assert summary.total_queries == 2
    assert summary.avg_faithfulness == 0.9
    assert summary.avg_answer_relevance == 0.9
    assert summary.avg_context_precision == 0.7
    assert summary.avg_latency_seconds == 0.4