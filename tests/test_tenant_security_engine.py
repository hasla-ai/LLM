import pytest
from src.core.tenant_security_engine import (
    MultiTenantIsolationEngine,
    TenantPolicy,
    SecurityContext,
)


def test_tenant_access_success():
    engine = MultiTenantIsolationEngine()
    policy = TenantPolicy(tenant_id="tenant_a", allowed_roles=["admin", "developer"])
    engine.register_tenant_policy(policy)

    context = SecurityContext(
        tenant_id="tenant_a",
        user_id="usr_123",
        role="developer",
        session_token="token_abc",
    )

    assert engine.validate_access(context) is True


def test_unregistered_tenant_rejection():
    engine = MultiTenantIsolationEngine()
    context = SecurityContext(
        tenant_id="unknown_tenant",
        user_id="usr_999",
        role="admin",
        session_token="token_xyz",
    )

    with pytest.raises(PermissionError, match="not registered"):
        engine.validate_access(context)


def test_unauthorized_role_rejection():
    engine = MultiTenantIsolationEngine()
    policy = TenantPolicy(tenant_id="tenant_b", allowed_roles=["admin"])
    engine.register_tenant_policy(policy)

    context = SecurityContext(
        tenant_id="tenant_b",
        user_id="usr_456",
        role="guest",
        session_token="token_123",
    )

    with pytest.raises(PermissionError, match="unauthorized"):
        engine.validate_access(context)


def test_rls_filter_generation():
    engine = MultiTenantIsolationEngine()
    policy = TenantPolicy(
        tenant_id="tenant_c",
        allowed_roles=["user"],
        custom_metadata_filter={"org_unit": "finance"},
    )
    engine.register_tenant_policy(policy)

    context = SecurityContext(
        tenant_id="tenant_c",
        user_id="usr_789",
        role="user",
        session_token="token_789",
    )

    rls_filter = engine.build_rls_filter(context)
    assert rls_filter["tenant_id"] == "tenant_c"
    assert rls_filter["org_unit"] == "finance"