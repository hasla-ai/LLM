from src.rag.vector_store import VectorStore
from src.rag.hybrid_search import BM25Retriever, HybridSearchEngine

def test_bm25_retriever_exact_keyword_match():
    retriever = BM25Retriever()
    docs = [
        {"id": "doc1", "text": "Error ERR-9021 occurred in production server"},
        {"id": "doc2", "text": "System health and performance monitoring metrics"}
    ]
    retriever.add_documents(docs)

    results = retriever.search("ERR-9021", top_k=1)
    assert len(results) == 1
    assert results[0]["id"] == "doc1"
    assert results[0]["bm25_score"] > 0.0

def test_hybrid_search_rrf_combination():
    store = VectorStore()
    # doc1 is semantically close to vector query [1.0, 0.0]
    store.add_document("doc1", "Artificial Intelligence and Machine Learning", [1.0, 0.0])
    # doc2 contains exact keyword 'ERR-404' but poor vector embedding [0.0, 1.0]
    store.add_document("doc2", "Database connection failed with code ERR-404", [0.0, 1.0])

    engine = HybridSearchEngine(vector_store=store)

    # Search with keyword "ERR-404" and query_embedding close to doc1
    hybrid_results = engine.search(
        query_text="Database ERR-404 issue",
        query_embedding=[0.1, 0.9],
        top_k=2
    )

    assert len(hybrid_results) == 2
    # doc2 should rank first due to strong BM25 keyword score overriding pure vector
    assert hybrid_results[0]["id"] == "doc2"
    assert "rrf_score" in hybrid_results[0]