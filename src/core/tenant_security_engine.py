import hashlib
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class TenantPolicy(BaseModel):
    """Encapsulates tenant-level security configuration & ACL policies."""
    tenant_id: str
    allowed_roles: List[str] = Field(default_factory=lambda: ["admin", "user"])
    enable_pii_sanitization: bool = True
    max_context_length: int = 8192
    custom_metadata_filter: Dict[str, Any] = Field(default_factory=dict)


class SecurityContext(BaseModel):
    """Runtime execution context representing the requesting tenant & user."""
    tenant_id: str
    user_id: str
    role: str
    session_token: str


class MultiTenantIsolationEngine:
    """
    Mission 28: Multi-Tenant Data Isolation & Security Policy Engine.
    Enforces Row-Level Security (RLS) for Vector/Graph retrieval and Tenant ACLs.
    """

    def __init__(self):
        self.policies: Dict[str, TenantPolicy] = {}

    def register_tenant_policy(self, policy: TenantPolicy) -> None:
        """Register or update tenant security policies."""
        self.policies[policy.tenant_id] = policy

    def validate_access(self, context: SecurityContext) -> bool:
        """Validates if the user context conforms to the tenant's security policy."""
        policy = self.policies.get(context.tenant_id)
        if not policy:
            raise PermissionError(f"Access Denied: Tenant '{context.tenant_id}' is not registered.")

        if context.role not in policy.allowed_roles:
            raise PermissionError(
                f"Access Denied: Role '{context.role}' unauthorized for Tenant '{context.tenant_id}'."
            )
        return True

    def build_rls_filter(self, context: SecurityContext) -> Dict[str, Any]:
        """
        Generates Row-Level Security (RLS) metadata filters for Vector RAG & Persistent Memory queries.
        Ensures strict tenant data boundary isolation.
        """
        self.validate_access(context)
        policy = self.policies[context.tenant_id]

        rls_filter = {
            "tenant_id": context.tenant_id,
            "visibility_level": "public" if context.role == "guest" else "restricted",
        }
        # Merge tenant-specific custom filters
        rls_filter.update(policy.custom_metadata_filter)
        return rls_filter

    def sanitize_tenant_payload(self, context: SecurityContext, payload: str) -> str:
        """Hashes or masks sensitive parameters based on tenant policy settings."""
        self.validate_access(context)
        policy = self.policies[context.tenant_id]

        if policy.enable_pii_sanitization:
            # Simple demonstration sanitizer: anonymize potential keys/secrets
            return payload.replace("SECRET_", "MASKED_")
        return payload