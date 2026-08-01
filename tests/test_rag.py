from unittest.mock import MagicMock
import pytest
from src.rag.vector_store import VectorStore, cosine_similarity
from src.rag.rag_pipeline import RAGPipeline, RAGResponse

def test_cosine_similarity_orthogonal_and_parallel():
    """Verify exact similarity calculations."""
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]
    
    assert cosine_similarity(v1, v2) == pytest.approx(1.0)
    assert cosine_similarity(v1, v3) == pytest.approx(0.0)

def test_vector_store_retrieval_ranking():
    """Verify document ranking order in similarity search."""
    store = VectorStore()
    store.add_document("doc1", "LLM Engineering involves RAG pipelines.", [1.0, 0.0, 0.0])
    store.add_document("doc2", "Making pizza requires dough and sauce.", [0.0, 1.0, 0.0])

    # Query embedding closer to doc1
    results = store.search(query_embedding=[0.9, 0.1, 0.0], top_k=1)
    
    assert len(results) == 1
    assert results[0]["id"] == "doc1"
    assert results[0]["score"] > 0.8

def test_rag_pipeline_synthesis_with_mock():
    """Verify end-to-end RAG workflow execution with mocked LLM."""
    mock_llm = MagicMock()
    expected_response = RAGResponse(
        answer="LLM engineering involves RAG systems and autonomous agents.",
        confidence=0.95,
        sources_used=["doc1"]
    )
    mock_llm.generate_structured.return_value = expected_response

    store = VectorStore()
    store.add_document("doc1", "LLM engineering involves RAG systems.", [1.0, 0.0])

    pipeline = RAGPipeline(llm_client=mock_llm, vector_store=store)
    response = pipeline.query("What is LLM engineering?", query_embedding=[1.0, 0.0])

    assert isinstance(response, RAGResponse)
    assert response.answer == "LLM engineering involves RAG systems and autonomous agents."
    assert "doc1" in response.sources_used
    assert response.confidence == 0.95