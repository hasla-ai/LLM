import math
import re
from typing import List, Dict, Any
from src.rag.vector_store import VectorStore

def tokenize(text: str) -> List[str]:
    """Simple alphanumeric tokenizer."""
    return re.findall(r'\w+', text.lower())

class BM25Retriever:
    """In-memory BM25 lexical retriever for exact keyword matching."""
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.documents: List[Dict[str, Any]] = []
        self.doc_len: List[int] = []
        self.avg_doc_len: float = 0.0
        self.doc_freqs: Dict[str, int] = {}
        self.corpus_size: int = 0

    def add_documents(self, docs: List[Dict[str, Any]]):
        self.documents = docs
        self.corpus_size = len(docs)
        self.doc_len = [len(tokenize(doc["text"])) for doc in docs]
        self.avg_doc_len = sum(self.doc_len) / self.corpus_size if self.corpus_size > 0 else 0.0

        self.doc_freqs = {}
        for doc in docs:
            tokens = set(tokenize(doc["text"]))
            for token in tokens:
                self.doc_freqs[token] = self.doc_freqs.get(token, 0) + 1

    def search(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        query_tokens = tokenize(query)
        scores = [0.0] * self.corpus_size

        for token in query_tokens:
            if token not in self.doc_freqs:
                continue
            
            # Inverse Document Frequency (IDF)
            df = self.doc_freqs[token]
            idf = math.log((self.corpus_size - df + 0.5) / (df + 0.5) + 1.0)

            for i, doc in enumerate(self.documents):
                doc_tokens = tokenize(doc["text"])
                tf = doc_tokens.count(token)
                if tf == 0:
                    continue

                # BM25 Term Weighting formula
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (self.doc_len[i] / self.avg_doc_len))
                scores[i] += idf * (numerator / denominator)

        scored_docs = [{**doc, "bm25_score": scores[i]} for i, doc in enumerate(self.documents)]
        scored_docs.sort(key=lambda x: x["bm25_score"], reverse=True)
        return scored_docs[:top_k]


class HybridSearchEngine:
    """Combines Dense Vector Search and BM25 Lexical Search using Reciprocal Rank Fusion (RRF)."""
    def __init__(self, vector_store: VectorStore, rrf_k: int = 60):
        self.vector_store = vector_store
        self.bm25_retriever = BM25Retriever()
        self.rrf_k = rrf_k

    def index_documents(self):
        """Indexes vector store documents into the BM25 retriever."""
        self.bm25_retriever.add_documents(self.vector_store.documents)

    def search(self, query_text: str, query_embedding: List[float], top_k: int = 2) -> List[Dict[str, Any]]:
        """Executes hybrid retrieval using Reciprocal Rank Fusion (RRF)."""
        # Ensure BM25 index is synced
        self.index_documents()

        vector_results = self.vector_store.search(query_embedding, top_k=len(self.vector_store.documents))
        bm25_results = self.bm25_retriever.search(query_text, top_k=len(self.vector_store.documents))

        rrf_scores: Dict[str, float] = {}
        doc_map: Dict[str, Dict[str, Any]] = {}

        # 1. RRF from Vector Search
        for rank, doc in enumerate(vector_results):
            doc_id = doc["id"]
            doc_map[doc_id] = doc
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (self.rrf_k + (rank + 1)))

        # 2. RRF from BM25 Search
        for rank, doc in enumerate(bm25_results):
            doc_id = doc["id"]
            doc_map[doc_id] = doc
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (1.0 / (self.rrf_k + (rank + 1)))

        # Sort by unified RRF score
        sorted_doc_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)

        return [{**doc_map[doc_id], "rrf_score": rrf_scores[doc_id]} for doc_id in sorted_doc_ids[:top_k]]