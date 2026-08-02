import pytest
from src.core.llm_gateway import (
    EnterpriseLLMGateway,
    QuotaExceeded,
    RateLimitExceeded,
    TenantContext,
    TokenBucketRateLimiter,
    UsageQuota,
)


@pytest.fixture
def sample_tenant():
    quota = UsageQuota(tenant_id="tenant_acme", max_rpm=2, max_tpm=500, monthly_budget_usd=10.0)
    return TenantContext(tenant_id="tenant_acme", api_key="sk-acme-secret", tier="enterprise", quota=quota)


def test_tenant_registration_and_request(sample_tenant):
    gateway = EnterpriseLLMGateway()
    gateway.register_tenant(sample_tenant)

    res = gateway.process_request(tenant_id="tenant_acme", prompt="Summarize enterprise architecture")
    assert res["tenant_id"] == "tenant_acme"
    assert res["provider"] == "primary_provider"
    assert res["remaining_budget_usd"] < 10.0


def test_rate_limiter_rpm_exceeded(sample_tenant):
    gateway = EnterpriseLLMGateway()
    gateway.register_tenant(sample_tenant)

    # Process allowed requests (max_rpm=2)
    gateway.process_request("tenant_acme", "Request 1")
    gateway.process_request("tenant_acme", "Request 2")

    # 3rd request should trigger RateLimitExceeded
    with pytest.raises(RateLimitExceeded):
        gateway.process_request("tenant_acme", "Request 3")


def test_quota_exceeded(sample_tenant):
    gateway = EnterpriseLLMGateway()
    sample_tenant.quota.monthly_budget_usd = 0.005
    gateway.register_tenant(sample_tenant)

    # Process first request costing $0.004
    gateway.process_request("tenant_acme", "Cheap Request", estimated_cost_usd=0.004)

    # Second request costing $0.004 should exceed $0.005 budget
    with pytest.raises(QuotaExceeded):
        gateway.process_request("tenant_acme", "Expensive Request", estimated_cost_usd=0.004)


def test_unregistered_tenant_error():
    gateway = EnterpriseLLMGateway()
    with pytest.raises(ValueError):
        gateway.process_request("unknown_tenant", "Hello world")