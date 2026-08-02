from unittest.mock import MagicMock
import pytest

from src.rag.multimodal_rag import (
    ModalityType,
    MultimodalDocument,
    MultimodalEmbedder,
    MultimodalRAGEngine,
    MultimodalVectorStore,
)


@pytest.fixture
def setup_multimodal_store():
    embedder = MultimodalEmbedder()
    store = MultimodalVectorStore()

    # Text document
    doc_text = MultimodalDocument(
        doc_id="doc_text_01",
        modality=ModalityType.TEXT,
        content="The quarterly revenue grew by 15% year-over-year.",
        embedding=embedder.embed_text("quarterly revenue growth 15%"),
    )

    # Image document (e.g., chart or diagram scan)
    doc_image = MultimodalDocument(
        doc_id="doc_img_01",
        modality=ModalityType.IMAGE,
        content="s3://data-bucket/charts/q3_revenue_bar_chart.png",
        embedding=embedder.embed_image("s3://data-bucket/charts/q3_revenue_bar_chart.png"),
    )

    store.add_document(doc_text)
    store.add_document(doc_image)
    return embedder, store


def test_multimodal_embedder_dimensions(setup_multimodal_store):
    embedder, _ = setup_multimodal_store
    text_vec = embedder.embed_text("test query")
    image_vec = embedder.embed_image("http://example.com/chart.png")

    assert len(text_vec) == 4
    assert len(image_vec) == 4


def test_multimodal_vector_store_search(setup_multimodal_store):
    embedder, store = setup_multimodal_store
    query_vec = embedder.embed_text("revenue growth")

    # Search all modalities
    results = store.search(query_vec, top_k=2)
    assert len(results) == 2

    # Filter strictly by IMAGE modality
    img_results = store.search(query_vec, top_k=2, modality_filter=ModalityType.IMAGE)
    assert len(img_results) == 1
    assert img_results[0][0].modality == ModalityType.IMAGE
    assert img_results[0][0].doc_id == "doc_img_01"


def test_multimodal_rag_engine_execution(setup_multimodal_store):
    embedder, store = setup_multimodal_store
    mock_llm = MagicMock()

    engine = MultimodalRAGEngine(
        embedder=embedder,
        vector_store=store,
        llm_client=mock_llm,
    )

    response = engine.run("What was the Q3 revenue growth?")

    assert response.query == "What was the Q3 revenue growth?"
    assert "doc_text_01" in response.retrieved_text_sources
    assert "doc_img_01" in response.retrieved_image_sources
    assert response.confidence_score >= 0.0