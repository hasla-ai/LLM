import re
from pydantic import BaseModel, Field

class GuardrailResult(BaseModel):
    """Result schema for guardrail checks."""
    is_safe: bool = Field(description="True if content passes all guardrail policies")
    violation_reason: str | None = Field(None, description="Detailed reason if policy failed")

class GuardrailEngine:
    """Fast pre/post execution safety checks."""
    
    PROMPT_INJECTION_PATTERNS = [
        r"ignore previous instructions",
        r"disregard all prior rules",
        r"you are now in developer mode",
    ]
    
    PII_PATTERNS = {
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
    }

    @classmethod
    def validate_input(cls, user_input: str) -> GuardrailResult:
        """Check for prompt injection attacks and malicious overrides."""
        lower_input = user_input.lower()
        for pattern in cls.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, lower_input):
                return GuardrailResult(
                    is_safe=False,
                    violation_reason=f"Prompt injection pattern detected: '{pattern}'"
                )
        return GuardrailResult(is_safe=True)

    @classmethod
    def sanitize_pii(cls, text: str) -> str:
        """Redact sensitive PII (emails, phone numbers) before LLM submission."""
        sanitized = text
        for pii_type, pattern in cls.PII_PATTERNS.items():
            sanitized = re.sub(pattern, f"[{pii_type.upper()}_REDACTED]", sanitized)
        return sanitized