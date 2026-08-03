from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class TokenDraft(BaseModel):
    """Speculatively generated token candidate sequence from a lightweight draft model."""
    draft_id: str
    tokens: List[str]
    confidence_scores: List[float]


class ValidationResult(BaseModel):
    """Payload representing tokens accepted or rejected by the target model."""
    accepted_tokens: List[str]
    num_accepted: int
    num_rejected: int
    acceptance_rate: float = Field(ge=0.0, le=1.0)


class SpeculativeDecoderEngine:
    """
    Mission 44: Real-Time Streaming Speculative Decoding & Draft Model Orchestrator.
    Generates fast draft token sequences and validates them in parallel against a target model.
    """

    def __init__(self, acceptance_threshold: float = 0.70):
        self.acceptance_threshold = acceptance_threshold

    def generate_draft_tokens(self, prompt: str, num_speculative_tokens: int = 5) -> TokenDraft:
        """Simulates speculative draft candidate generation via a lightweight model."""
        words = prompt.strip().split()
        draft_tokens = [f"token_{i}" for i in range(num_speculative_tokens)]
        # Default high confidence score mock
        confidences = [0.85 - (i * 0.05) for i in range(num_speculative_tokens)]

        return TokenDraft(
            draft_id="draft_001",
            tokens=draft_tokens,
            confidence_scores=confidences
        )

    def validate_draft(self, draft: TokenDraft) -> ValidationResult:
        """
        Validates draft tokens against target model acceptance thresholds.
        Returns accepted token sequence up to the first rejected candidate.
        """
        accepted: List[str] = []
        rejected_count = 0

        for token, score in zip(draft.tokens, draft.confidence_scores):
            if score >= self.acceptance_threshold:
                accepted.append(token)
            else:
                # In speculative decoding, validation stops at the first rejected token
                rejected_count = len(draft.tokens) - len(accepted)
                break

        total = len(draft.tokens)
        rate = len(accepted) / total if total > 0 else 0.0

        return ValidationResult(
            accepted_tokens=accepted,
            num_accepted=len(accepted),
            num_rejected=rejected_count,
            acceptance_rate=round(rate, 4)
        )