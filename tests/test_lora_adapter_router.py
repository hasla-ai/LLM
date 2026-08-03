import unittest
from src.core.lora_adapter_router import (
    LoRAAdapterRouter,
    LoRAAdapterConfig,
    DomainTaskType,
)


class TestLoRAAdapterRouter(unittest.TestCase):
    def setUp(self):
        self.router = LoRAAdapterRouter(base_model_name="qwen-2.5-7b")

        # Shared Enterprise Adapters
        self.shared_code_adapter = LoRAAdapterConfig(
            adapter_id="lora-shared-code-v1",
            domain_type=DomainTaskType.CODE_GEN,
            weight_path="/weights/code_v1.safetensors",
        )
        self.router.register_adapter(self.shared_code_adapter)

        # Tenant Alpha Custom Legal Adapter
        self.tenant_alpha_legal_adapter = LoRAAdapterConfig(
            adapter_id="lora-alpha-legal-v2",
            domain_type=DomainTaskType.LEGAL_REASONING,
            tenant_id="tenant_alpha",
            weight_path="/weights/alpha_legal_v2.safetensors",
        )
        self.router.register_adapter(self.tenant_alpha_legal_adapter)

    def test_select_tenant_specific_adapter(self):
        adapter = self.router.select_optimal_adapter(
            task_type=DomainTaskType.LEGAL_REASONING,
            tenant_id="tenant_alpha"
        )
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.adapter_id, "lora-alpha-legal-v2")

    def test_fallback_to_shared_adapter(self):
        adapter = self.router.select_optimal_adapter(
            task_type=DomainTaskType.CODE_GEN,
            tenant_id="tenant_beta"  # Beta has no custom adapter, falls back to shared
        )
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter.adapter_id, "lora-shared-code-v1")

    def test_hot_swap_execution(self):
        swap_message = self.router.hot_swap_adapter("lora-shared-code-v1")
        self.assertIn("Successfully hot-swapped", swap_message)
        self.assertEqual(self.router.active_adapter_id, "lora-shared-code-v1")
        self.assertTrue(self.shared_code_adapter.is_loaded)


if __name__ == "__main__":
    unittest.main()