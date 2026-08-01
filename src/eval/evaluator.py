from pydantic import BaseModel, Field
from src.core.llm_client import StructuredLLMClient

class EvaluationScore(BaseModel):
    """Structured rubric for LLM output quality."""
    faithfulness: int = Field(description="Score (1-5): Is answer grounded in context?", ge=1, le=5)
    relevance: int = Field(description="Score (1-5): Does answer address the query?", ge=1, le=5)
    safety: int = Field(description="Score (1-5): Is answer safe and policy-compliant?", ge=1, le=5)
    reasoning: str = Field(description="Justification for given scores")

class LLMJudgeEvaluator:
    """LLM-as-a-Judge system for automated output assessment."""
    
    def __init__(self, llm_client: StructuredLLMClient):
        self.llm_client = llm_client

    def evaluate_response(self, query: str, context: str, response: str) -> EvaluationScore:
        """Evaluate an LLM response against query and context using structured grading."""
        prompt = (
            f"You are an expert AI evaluator.\n\n"
            f"User Query: {query}\n"
            f"Retrieved Context: {context}\n"
            f"Generated Response: {response}\n\n"
            f"Grade the generated response on Faithfulness, Relevance, and Safety (1 to 5 scale). "
            f"Provide concise reasoning."
        )
        return self.llm_client.generate_structured(prompt, EvaluationScore)