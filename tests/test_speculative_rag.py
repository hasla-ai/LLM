from unittest.mock import MagicMock
import pytest
from src.rag.speculative_rag import (
    SpeculativeRAGPipeline,
    DraftAnswer,
    VerificationResult,
    SpeculativeRAGResponse
)
from src.rag.vector_store import VectorStore


@pytest.fixture
def mock_vector_store():
    vs = MagicMock(spec=VectorStore)
    vs.search.return_value = [
        {"id": "doc_1", "content": "Speculative RAG uses a fast draft model and a verifier model."}
    ]
    return vs


def test_speculative_rag_draft_accepted(mock_vector_store):
    draft_client = MagicMock()
    verifier_client = MagicMock()

    # Fast draft return
    draft_client.generate.return_value = DraftAnswer(
        candidate_text="Speculative RAG combines small draft models with verifiers.",
        confidence_score=0.9
    )

    # Verifier accepts draft
    verifier_client.generate.return_value = VerificationResult(
        is_accepted=True,
        verdict_score=0.95,
        corrected_answer=None,
        reasoning="Draft is accurate and supported by context."
    )

    pipeline = SpeculativeRAGPipeline(
        draft_client=draft_client,
        verifier_client=verifier_client,
        vector_store=mock_vector_store,
        acceptance_threshold=0.8
    )

    response = pipeline.run("What is Speculative RAG?")

    assert isinstance(response, SpeculativeRAGResponse)
    assert response.was_draft_accepted is True
    assert response.final_answer == "Speculative RAG combines small draft models with verifiers."
    assert "doc_1" in response.sources


def test_speculative_rag_draft_rejected_and_corrected(mock_vector_store):
    draft_client = MagicMock()
    verifier_client = MagicMock()

    # Draft has inaccurate details
    draft_client.generate.return_value = DraftAnswer(
        candidate_text="Speculative RAG uses quantum computing.",
        confidence_score=0.4
    )

    # Verifier rejects draft and offers correction
    verifier_client.generate.return_value = VerificationResult(
        is_accepted=False,
        verdict_score=0.2,
        corrected_answer="Speculative RAG uses a fast draft model alongside a verifier model.",
        reasoning="Quantum computing is not mentioned in context."
    )

    pipeline = SpeculativeRAGPipeline(
        draft_client=draft_client,
        verifier_client=verifier_client,
        vector_store=mock_vector_store,
        acceptance_threshold=0.8
    )

    response = pipeline.run("What is Speculative RAG?")

    assert response.was_draft_accepted is False
    assert response.final_answer == "Speculative RAG uses a fast draft model alongside a verifier model."