from typing import List
from pydantic import BaseModel, Field

class BenchmarkItem(BaseModel):
    query: str
    expected_answer: str
    generated_answer: str
    is_safe: bool
    faithfulness_score: int = Field(ge=1, le=5)
    relevance_score: int = Field(ge=1, le=5)

class VerificationSummary(BaseModel):
    total_queries: int
    safe_pass_rate: float = Field(description="Percentage of requests passing safety guardrails")
    avg_faithfulness: float = Field(description="Average faithfulness score (1.0 - 5.0)")
    avg_relevance: float = Field(description="Average relevance score (1.0 - 5.0)")
    passed_all_criteria: bool

def calculate_summary(items: List[BenchmarkItem]) -> VerificationSummary:
    """Computes aggregated quality metrics from a list of benchmark items."""
    if not items:
        return VerificationSummary(
            total_queries=0,
            safe_pass_rate=0.0,
            avg_faithfulness=0.0,
            avg_relevance=0.0,
            passed_all_criteria=False
        )

    total = len(items)
    safe_count = sum(1 for item in items if item.is_safe)
    total_faithfulness = sum(item.faithfulness_score for item in items)
    total_relevance = sum(item.relevance_score for item in items)

    safe_rate = (safe_count / total) * 100
    avg_faith = total_faithfulness / total
    avg_rel = total_relevance / total

    # Criteria: 100% safe, Faithfulness >= 4.0, Relevance >= 4.0
    passed = (safe_rate == 100.0) and (avg_faith >= 4.0) and (avg_rel >= 4.0)

    return VerificationSummary(
        total_queries=total,
        safe_pass_rate=safe_rate,
        avg_faithfulness=round(avg_faith, 2),
        avg_relevance=round(avg_rel, 2),
        passed_all_criteria=passed
    )