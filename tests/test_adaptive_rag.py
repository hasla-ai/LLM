from unittest.mock import MagicMock
import pytest
from src.rag.adaptive_rag import (
    AdaptiveRAGEngine,
    RoutingDecision,
    ComplexityTier,
    AdaptiveRAGResponse
)
from src.rag.vector_store import VectorStore
from src.rag.rag_pipeline import RAGPipeline, RAGResponse
from src.rag.agentic_rag import AgenticRAGEngine, AgenticRAGResponse, QueryPlan


@pytest.fixture
def mock_vector_store():
    return MagicMock(spec=VectorStore)


def test_adaptive_rag_routing_simple_no_rag(mock_vector_store):
    llm_client = MagicMock()

    # Step 1: Router classifies as SIMPLE_NO_RAG
    routing = RoutingDecision(
        complexity_tier=ComplexityTier.SIMPLE_NO_RAG,
        reasoning="Math question requires no external search."
    )

    # Step 2: Direct answer
    DirectAns = MagicMock()
    DirectAns.answer = "15 * 12 = 180"

    llm_client.generate.side_effect = [routing, DirectAns]

    engine = AdaptiveRAGEngine(llm_client=llm_client, vector_store=mock_vector_store)
    response = engine.run("What is 15 multiplied by 12?")

    assert isinstance(response, AdaptiveRAGResponse)
    assert response.complexity_tier == ComplexityTier.SIMPLE_NO_RAG
    assert response.final_answer == "15 * 12 = 180"
    assert len(response.sources) == 0


def test_adaptive_rag_routing_single_step_rag(mock_vector_store):
    llm_client = MagicMock()

    routing = RoutingDecision(
        complexity_tier=ComplexityTier.SINGLE_STEP_RAG,
        reasoning="Factual query targeting internal document context."
    )
    llm_client.generate.return_value = routing

    mock_rag_pipeline = MagicMock()
    mock_rag_response = MagicMock()
    mock_rag_response.answer = "Refunds are processed within 14 days."
    mock_rag_response.sources = ["doc_policy"]
    mock_rag_response.sources_used = ["doc_policy"]
    
    # Configure mock_rag_pipeline to return mock_rag_response on any method call
    mock_rag_pipeline.run.return_value = mock_rag_response
    mock_rag_pipeline.generate_answer.return_value = mock_rag_response

    engine = AdaptiveRAGEngine(
        llm_client=llm_client,
        vector_store=mock_vector_store,
        rag_pipeline=mock_rag_pipeline
    )
    response = engine.run("What is the refund policy?")

    assert response.complexity_tier == ComplexityTier.SINGLE_STEP_RAG
    assert response.final_answer == "Refunds are processed within 14 days."


def test_adaptive_rag_routing_complex_multi_step_rag(mock_vector_store):
    llm_client = MagicMock()

    routing = RoutingDecision(
        complexity_tier=ComplexityTier.COMPLEX_MULTI_STEP_RAG,
        reasoning="Comparative multi-part query requiring decomposition."
    )
    llm_client.generate.return_value = routing

    mock_agentic_engine = MagicMock(spec=AgenticRAGEngine)
    mock_plan = QueryPlan(
        original_query="Compare Company A and B revenue.",
        reasoning="Decompose into sub-queries.",
        sub_queries=[]
    )
    mock_agentic_engine.run.return_value = AgenticRAGResponse(
        original_query="Compare Company A and B revenue.",
        query_plan=mock_plan,
        sub_query_results=[],
        final_answer="Company A revenue grew 15% while Company B grew 8%.",
        aggregated_source_ids=["doc_comp_a", "doc_comp_b"]
    )

    engine = AdaptiveRAGEngine(
        llm_client=llm_client,
        vector_store=mock_vector_store,
        agentic_rag_engine=mock_agentic_engine
    )
    response = engine.run("Compare Company A and Company B Q3 revenue.")

    assert response.complexity_tier == ComplexityTier.COMPLEX_MULTI_STEP_RAG
    assert "Company A revenue grew 15%" in response.final_answer
    assert "doc_comp_a" in response.sources
    assert mock_agentic_engine.run.called