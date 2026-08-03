import unittest
import time
from src.core.tenant_priority_scheduler import (
    TenantPriorityScheduler,
    TenantTier,
)


class TestTenantPriorityScheduler(unittest.TestCase):
    def setUp(self):
        self.scheduler = TenantPriorityScheduler()
        self.scheduler.register_tenant("enterprise_client", tier=TenantTier.ENTERPRISE)
        self.scheduler.register_tenant("free_client", tier=TenantTier.FREE)

    def test_priority_levels(self):
        self.assertEqual(
            self.scheduler.get_tenant_priority("enterprise_client"), 100
        )
        self.assertEqual(self.scheduler.get_tenant_priority("free_client"), 10)

    def test_rate_limit_enforcement(self):
        # Free client limit is 5000 tokens per minute
        allowed = self.scheduler.check_rate_limit("free_client", requested_tokens=4000)
        self.assertTrue(allowed)

        # Exceeding limit should return False
        blocked = self.scheduler.check_rate_limit("free_client", requested_tokens=2000)
        self.assertFalse(blocked)

    def test_cost_attribution_calculation(self):
        metrics = self.scheduler.record_cost_attribution(
            tenant_id="enterprise_client",
            prompt_tokens=1000,     # $0.0025
            completion_tokens=2000  # $0.0200
        )
        self.assertEqual(metrics.total_prompt_tokens, 1000)
        self.assertEqual(metrics.total_completion_tokens, 2000)
        self.assertAlmostEqual(metrics.estimated_cost_usd, 0.0225, places=4)


if __name__ == "__main__":
    unittest.main()