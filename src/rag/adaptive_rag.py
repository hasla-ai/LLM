from enum Enum
from typing import List, Optional, Any
from pydantic import BaseModel, Field
from src.core.llm_client import StructuredLLMClient
from src.rag.vector_store import VectorStore
from src.rag.rag_pipeline import RAGPipeline
from src.rag.agentic_rag import AgenticRAGEngine


class ComplexityTier(str, Enum):
    SIMPLE_NO_RAG = "SIMPLE_NO_RAG"          # Parametric knowledge, greetings, simple logic
    SINGLE_STEP_RAG = "SINGLE_STEP_RAG"      # Direct factual questions requiring document retrieval
    COMPLEX_MULTI_STEP_RAG = "COMPLEX_MULTI_STEP_RAG"  # Multi-part, comparative, or reasoning-heavy questions


class RoutingDecision(BaseModel):
    """Classification decision produced by the query router."""
    complexity_tier: ComplexityTier = Field(..., description="Chosen execution tier based on prompt analysis.")
    reasoning: str = Field(..., description="Explanation for assigning this complexity tier.")


class AdaptiveRAGResponse(BaseModel):
    """Final output payload containing the answer and operational metadata."""
    query: str
    complexity_tier: ComplexityTier
    routing_reasoning: str
    final_answer: str
    sources: List[str]


class AdaptiveRAGEngine:
    """Adaptive RAG Engine dynamically routing queries based on upfront complexity classification."""

    ROUTER_SYSTEM_PROMPT = """
You are an expert query router for an adaptive AI search platform. Analyze the incoming user prompt and classify its complexity into exactly one tier:
1. SIMPLE_NO_RAG: General knowledge, greetings, math, or basic reasoning requiring NO external document search.
2. SINGLE_STEP_RAG: Direct factual questions targeting specific documents or stored context.
3. COMPLEX_MULTI_STEP_RAG: Comparative, multi-faceted, or analytical questions requiring decomposed sub-queries or multi-step research.
"""

    def __init__(
        self,
        llm_client: StructuredLLMClient,
        vector_store: VectorStore,
        rag_pipeline: Optional[RAGPipeline] = None,
        agentic_rag_engine: Optional[AgenticRAGEngine] = None
    ):
        self.llm_client = llm_client
        self.vector_store = vector_store
        self.rag_pipeline = rag_pipeline or RAGPipeline(llm_client=llm_client, vector_store=vector_store)
        self.agentic_rag_engine = agentic_rag_engine or AgenticRAGEngine(llm_client=llm_client, vector_store=vector_store)

    def classify_query(self, query: str) -> RoutingDecision:
        """Classifies query complexity to determine the execution path."""
        user_prompt = f"Analyze and classify this query: {query}"
        return self.llm_client.generate(
            prompt=user_prompt,
            response_schema=RoutingDecision,
            system_prompt=self.ROUTER_SYSTEM_PROMPT
        )

    def run(self, query: str) -> AdaptiveRAGResponse:
        """Executes the optimal strategy tier based on classified query complexity."""
        decision = self.classify_query(query)

        if decision.complexity_tier == ComplexityTier.SIMPLE_NO_RAG:
            # Fast-Path: Direct generation without retrieval overhead
            class DirectAnswer(BaseModel):
                answer: str

            direct_result = self.llm_client.generate(
                prompt=query,
                response_schema=DirectAnswer
            )
            return AdaptiveRAGResponse(
                query=query,
                complexity_tier=decision.complexity_tier,
                routing_reasoning=decision.reasoning,
                final_answer=direct_result.answer,
                sources=[]
            )

        elif decision.complexity_tier == ComplexityTier.SINGLE_STEP_RAG:
            # Mid-Path: Standard single-pass vector/context retrieval
            rag_res = self.rag_pipeline.run(query)
            return AdaptiveRAGResponse(
                query=query,
                complexity_tier=decision.complexity_tier,
                routing_reasoning=decision.reasoning,
                final_answer=rag_res.answer,
                sources=rag_res.sources
            )

        else:  # COMPLEX_MULTI_STEP_RAG
            # Deep-Path: Agentic query decomposition & multi-pass sub-query execution
            agentic_res = self.agentic_rag_engine.run(query)
            return AdaptiveRAGResponse(
                query=query,
                complexity_tier=decision.complexity_tier,
                routing_reasoning=decision.reasoning,
                final_answer=agentic_res.final_answer,
                sources=agentic_res.aggregated_source_ids
            )