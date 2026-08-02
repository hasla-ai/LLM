import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RateLimitExceeded(Exception):
    """Raised when tenant exceeds RPM or TPM limits."""
    pass


class QuotaExceeded(Exception):
    """Raised when tenant exceeds maximum allowed token or monetary budget."""
    pass


class UsageQuota(BaseModel):
    """Defines usage limits for a specific tenant."""
    tenant_id: str
    max_rpm: int = Field(default=60, description="Requests Per Minute limit")
    max_tpm: int = Field(default=100_000, description="Tokens Per Minute limit")
    monthly_budget_usd: float = Field(default=100.0, description="Monthly USD spend cap")
    current_month_spend_usd: float = Field(default=0.0, description="Current accumulated spend")


class TenantContext(BaseModel):
    """Context holding tenant credentials and current usage state."""
    tenant_id: str
    api_key: str
    tier: str = Field(default="standard")
    quota: UsageQuota


class TokenBucketRateLimiter:
    """Implements sliding token bucket rate limiting for RPM and TPM."""

    def __init__(self):
        # Maps tenant_id -> {"last_refill": timestamp, "tokens_rpm": count, "tokens_tpm": count}
        self.state: Dict[str, Dict[str, Any]] = {}

    def _get_or_create_state(self, tenant: TenantContext, now: float) -> Dict[str, Any]:
        if tenant.tenant_id not in self.state:
            self.state[tenant.tenant_id] = {
                "last_refill": now,
                "current_rpm": tenant.quota.max_rpm,
                "current_tpm": tenant.quota.max_tpm,
            }
        return self.state[tenant.tenant_id]

    def check_and_consume(self, tenant: TenantContext, estimated_tokens: int) -> bool:
        """Consumes rate limit tokens if available. Returns True or raises RateLimitExceeded."""
        now = time.time()
        bucket = self._get_or_create_state(tenant, now)

        # Calculate time elapsed and refill buckets
        elapsed = now - bucket["last_refill"]
        if elapsed >= 60.0:
            bucket["current_rpm"] = tenant.quota.max_rpm
            bucket["current_tpm"] = tenant.quota.max_tpm
            bucket["last_refill"] = now

        if bucket["current_rpm"] < 1:
            raise RateLimitExceeded(f"Tenant '{tenant.tenant_id}' exceeded RPM limit ({tenant.quota.max_rpm} req/min).")

        if bucket["current_tpm"] < estimated_tokens:
            raise RateLimitExceeded(f"Tenant '{tenant.tenant_id}' exceeded TPM limit ({tenant.quota.max_tpm} tok/min).")

        bucket["current_rpm"] -= 1
        bucket["current_tpm"] -= estimated_tokens
        return True


class EnterpriseLLMGateway:
    """Multi-tenant gateway providing rate limiting, cost control, and provider fallback."""

    def __init__(self, rate_limiter: Optional[TokenBucketRateLimiter] = None):
        self.rate_limiter = rate_limiter or TokenBucketRateLimiter()
        self.tenants: Dict[str, TenantContext] = {}
        self.providers: List[str] = ["primary_provider", "secondary_fallback_provider"]

    def register_tenant(self, tenant: TenantContext) -> None:
        """Registers a tenant with quota limits into the gateway registry."""
        self.tenants[tenant.tenant_id] = tenant

    def process_request(
        self,
        tenant_id: str,
        prompt: str,
        estimated_tokens: int = 150,
        estimated_cost_usd: float = 0.002,
    ) -> Dict[str, Any]:
        """Validates, rate limits, meters, and routes an LLM request with provider fallback."""
        if tenant_id not in self.tenants:
            raise ValueError(f"Unknown or unauthorized tenant ID: '{tenant_id}'")

        tenant = self.tenants[tenant_id]

        # 1. Budget Quota Check
        if tenant.quota.current_month_spend_usd + estimated_cost_usd > tenant.quota.monthly_budget_usd:
            raise QuotaExceeded(
                f"Tenant '{tenant_id}' monthly budget limit of ${tenant.quota.monthly_budget_usd:.2f} exceeded."
            )

        # 2. Rate Limiting Check
        self.rate_limiter.check_and_consume(tenant, estimated_tokens)

        # 3. Provider Routing with Fallback Execution
        executed_provider = None
        response_text = None

        for provider in self.providers:
            try:
                # Simulate primary provider dispatch
                executed_provider = provider
                response_text = f"[{executed_provider}] Echo response for prompt: '{prompt[:30]}...'"
                break
            except Exception:
                continue

        # 4. Record usage
        tenant.quota.current_month_spend_usd += estimated_cost_usd

        return {
            "tenant_id": tenant_id,
            "provider": executed_provider,
            "response": response_text,
            "tokens_consumed": estimated_tokens,
            "cost_usd": estimated_cost_usd,
            "remaining_budget_usd": tenant.quota.monthly_budget_usd - tenant.quota.current_month_spend_usd,
        }