import enum
import time
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class TenantTier(str, enum.Enum):
    ENTERPRISE = "enterprise"
    PRO = "pro"
    FREE = "free"


class TenantCostMetrics(BaseModel):
    """Real-time token usage and cost attribution payload."""
    tenant_id: str
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    estimated_cost_usd: float = 0.0


class TenantRateLimitConfig(BaseModel):
    """Rate limit and token allocation limits per tenant tier."""
    tier: TenantTier
    max_tokens_per_minute: int
    priority_level: int  # Higher value = higher priority queueing


TIER_CONFIGS: Dict[TenantTier, TenantRateLimitConfig] = {
    TenantTier.ENTERPRISE: TenantRateLimitConfig(
        tier=TenantTier.ENTERPRISE, max_tokens_per_minute=100_000, priority_level=100
    ),
    TenantTier.PRO: TenantRateLimitConfig(
        tier=TenantTier.PRO, max_tokens_per_minute=25_000, priority_level=50
    ),
    TenantTier.FREE: TenantRateLimitConfig(
        tier=TenantTier.FREE, max_tokens_per_minute=5_000, priority_level=10
    ),
}

# Cost per 1K tokens in USD (e.g., GPT-4o tier pricing)
PROMPT_COST_PER_1K = 0.0025
COMPLETION_COST_PER_1K = 0.0100


class TenantPriorityScheduler:
    """
    Mission 37: Multi-Tenant Token Rate Limiter, Priority Scheduler & Cost Allocation Mesh.
    Manages SLA rate limiting, priority scheduling under GPU load, and multi-tenant billing metrics.
    """

    def __init__(self):
        self._tenant_usage: Dict[str, Dict[str, float]] = {}
        self._tenant_tiers: Dict[str, TenantTier] = {}
        self._cost_metrics: Dict[str, TenantCostMetrics] = {}

    def register_tenant(self, tenant_id: str, tier: TenantTier = TenantTier.FREE):
        """Registers a tenant with a assigned tier for rate limits and priority scheduling."""
        self._tenant_tiers[tenant_id] = tier
        if tenant_id not in self._cost_metrics:
            self._cost_metrics[tenant_id] = TenantCostMetrics(tenant_id=tenant_id)
        if tenant_id not in self._tenant_usage:
            self._tenant_usage[tenant_id] = {"tokens": 0, "last_reset": time.time()}

    def check_rate_limit(self, tenant_id: str, requested_tokens: int) -> bool:
        """
        Evaluates token bucket rate limit based on tenant tier limits.
        Resets token counts every minute.
        """
        tier = self._tenant_tiers.get(tenant_id, TenantTier.FREE)
        config = TIER_CONFIGS[tier]
        usage = self._tenant_usage.get(
            tenant_id, {"tokens": 0, "last_reset": time.time()}
        )

        now = time.time()
        # Reset bucket if 60 seconds elapsed
        if now - usage["last_reset"] >= 60.0:
            usage["tokens"] = 0
            usage["last_reset"] = now

        if usage["tokens"] + requested_tokens > config.max_tokens_per_minute:
            return False

        usage["tokens"] += requested_tokens
        self._tenant_usage[tenant_id] = usage
        return True

    def record_cost_attribution(
        self, tenant_id: str, prompt_tokens: int, completion_tokens: int
    ) -> TenantCostMetrics:
        """Accrues token consumption and computes precise micro-USD billing costs."""
        metrics = self._cost_metrics.get(
            tenant_id, TenantCostMetrics(tenant_id=tenant_id)
        )

        metrics.total_prompt_tokens += prompt_tokens
        metrics.total_completion_tokens += completion_tokens

        prompt_cost = (prompt_tokens / 1000.0) * PROMPT_COST_PER_1K
        completion_cost = (completion_tokens / 1000.0) * COMPLETION_COST_PER_1K
        metrics.estimated_cost_usd += round(prompt_cost + completion_cost, 6)

        self._cost_metrics[tenant_id] = metrics
        return metrics

    def get_tenant_priority(self, tenant_id: str) -> int:
        """Returns the scheduling priority level for GPU queue arbitration."""
        tier = self._tenant_tiers.get(tenant_id, TenantTier.FREE)
        return TIER_CONFIGS[tier].priority_level