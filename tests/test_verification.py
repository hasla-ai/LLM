from unittest.mock import MagicMock
from src.verification.metrics import BenchmarkItem, calculate_summary
from src.verification.benchmark_runner import ContinuousVerificationRunner
from src.eval.evaluator import EvaluationScore

def test_metrics_calculation_passing():
    items = [
        BenchmarkItem(
            query="What is RAG?",
            expected_answer="RAG is Retrieval-Augmented Generation.",
            generated_answer="RAG is Retrieval-Augmented Generation.",
            is_safe=True,
            faithfulness_score=5,
            relevance_score=5
        )
    ]
    summary = calculate_summary(items)
    assert summary.safe_pass_rate == 100.0
    assert summary.avg_faithfulness == 5.0
    assert summary.passed_all_criteria is True

def test_benchmark_runner_execution_with_mock():
    mock_judge = MagicMock()
    mock_judge.evaluate_response.return_value = EvaluationScore(
        faithfulness=5,
        relevance=5,
        safety=5,
        reasoning="Perfect alignment."
    )

    runner = ContinuousVerificationRunner(judge_evaluator=mock_judge)
    dataset = [
        {
            "query": "Explain LLM Agents.",
            "context": "Agents use tools and decision loops.",
            "generated_answer": "Agents utilize tool calling and loops.",
            "expected_answer": "Agents use tools and loops."
        }
    ]

    summary = runner.run_benchmark(dataset)
    assert summary.total_queries == 1
    assert summary.passed_all_criteria is True