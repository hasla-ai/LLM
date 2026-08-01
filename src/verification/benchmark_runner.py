import json
from typing import List, Dict, Any
from src.eval.guardrails import GuardrailEngine
from src.eval.evaluator import LLMJudgeEvaluator
from src.verification.metrics import BenchmarkItem, VerificationSummary, calculate_summary

class ContinuousVerificationRunner:
    """Orchestrates end-to-end regression benchmarks across system modules."""

    def __init__(self, judge_evaluator: LLMJudgeEvaluator):
        self.judge = judge_evaluator

    def run_benchmark(self, dataset: List[Dict[str, Any]]) -> VerificationSummary:
        """Executes full evaluation loop over test dataset items."""
        benchmark_items: List[BenchmarkItem] = []

        for entry in dataset:
            query = entry["query"]
            context = entry["context"]
            generated_answer = entry["generated_answer"]
            expected_answer = entry["expected_answer"]

            # 1. Verify Input Guardrails
            guardrail_res = GuardrailEngine.validate_input(query)

            # 2. Judge Evaluation
            eval_score = self.judge.evaluate_response(
                query=query,
                context=context,
                response=generated_answer
            )

            benchmark_items.append(
                BenchmarkItem(
                    query=query,
                    expected_answer=expected_answer,
                    generated_answer=generated_answer,
                    is_safe=guardrail_res.is_safe,
                    faithfulness_score=eval_score.faithfulness,
                    relevance_score=eval_score.relevance
                )
            )

        return calculate_summary(benchmark_items)

    def export_report(self, summary: VerificationSummary, output_path: str = "benchmark_report.json"):
        """Exports verification results to JSON report file."""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(summary.model_dump_json(indent=2))