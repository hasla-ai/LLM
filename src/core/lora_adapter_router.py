import enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class DomainTaskType(str, enum.Enum):
    GENERAL = "general"
    CODE_GEN = "code_generation"
    LEGAL_REASONING = "legal_reasoning"
    MEDICAL_QA = "medical_qa"
    FINANCIAL_ANALYSIS = "financial_analysis"


class LoRAAdapterConfig(BaseModel):
    """Metadata schema for a lightweight LoRA Adapter weight checkpoint."""
    adapter_id: str
    domain_type: DomainTaskType
    rank_r: int = 8
    alpha: float = 16.0
    weight_path: str
    tenant_id: Optional[str] = None  # None indicates shared enterprise adapter
    is_loaded: bool = False


class LoRAAdapterRouter:
    """
    Mission 29: Dynamic Fine-Tuning & Adaptive LoRA Adapter Router.
    Hot-swaps LoRA domain weights in runtime context based on task intent and tenant clearance.
    """

    def __init__(self, base_model_name: str = "qwen-2.5-coder-7b"):
        self.base_model_name = base_model_name
        self.registered_adapters: Dict[str, LoRAAdapterConfig] = {}
        self.active_adapter_id: Optional[str] = None

    def register_adapter(self, config: LoRAAdapterConfig) -> None:
        """Register a fine-tuned LoRA adapter into the runtime pool."""
        self.registered_adapters[config.adapter_id] = config

    def select_optimal_adapter(
        self,
        task_type: DomainTaskType,
        tenant_id: str
    ) -> Optional[LoRAAdapterConfig]:
        """
        Selects the most specific adapter for a tenant and domain task.
        Prioritizes Tenant-Specific Domain Adapters over Shared Enterprise Domain Adapters.
        """
        # 1. Search for Tenant-Specific Domain Adapter
        for adapter in self.registered_adapters.values():
            if adapter.tenant_id == tenant_id and adapter.domain_type == task_type:
                return adapter

        # 2. Fallback to Shared Enterprise Domain Adapter
        for adapter in self.registered_adapters.values():
            if adapter.tenant_id is None and adapter.domain_type == task_type:
                return adapter

        # 3. Default: No adapter needed (Use Base Model)
        return None

    def hot_swap_adapter(self, adapter_id: Optional[str]) -> str:
        """
        Simulates low-latency runtime hot-swapping of LoRA weights without reloading the base LLM.
        """
        if adapter_id is None:
            self.active_adapter_id = None
            return f"Unloaded adapters. Active runtime model: Base ({self.base_model_name})"

        if adapter_id not in self.registered_adapters:
            raise ValueError(f"Adapter ID '{adapter_id}' not found in registry.")

        # Simulate unloading previous adapter and activating target adapter
        if self.active_adapter_id and self.active_adapter_id in self.registered_adapters:
            self.registered_adapters[self.active_adapter_id].is_loaded = False

        selected = self.registered_adapters[adapter_id]
        selected.is_loaded = True
        self.active_adapter_id = adapter_id

        return f"Successfully hot-swapped LoRA Adapter '{adapter_id}' (Rank: {selected.rank_r}, Alpha: {selected.alpha}) onto Base ({self.base_model_name})"