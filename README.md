# 🚀 LLM Engineering Lab (`llm-engineering-lab`)

A hands-on, test-driven repository for building production-grade LLM applications, RAG pipelines, and Autonomous Agent systems.

Every module in this repository is built with **strict type validation (Pydantic)**, **Docker containerization**, and **automated Pytest suites**.

---

## 📂 Project Structure

```text
llm-engineering-lab/
├── Dockerfile                  # Containerized runtime for isolated execution
├── pyproject.toml              # Dependencies & Pytest configuration
├── requirements.txt            # Python package requirements
├── ARCHITECTURE.md             # System architecture & data flow design
├── src/
│   ├── core/                   # Structured LLM inference engine
│   │   ├── __init__.py
│   │   └── llm_client.py       # Pydantic-enforced Structured LLM Client
│   ├── rag/                    # Retrieval-Augmented Generation pipeline
│   │   ├── __init__.py
│   │   ├── vector_store.py     # In-Memory Vector Store & Cosine Similarity engine
│   │   ├── rag_pipeline.py     # Context retrieval & synthesis orchestrator
│   │   └── hybrid_search.py    # BM25 + Vector Search with Reciprocal Rank Fusion
│   ├── agent/                  # Autonomous Tool-Calling & Multi-Agent Graph
│   │   ├── __init__.py
│   │   ├── tools.py            # Tool registry & execution functions
│   │   ├── agent_engine.py     # ReAct-style Agent decision loop
│   │   └── graph_orchestrator.py # Mission 7: Stateful Graph Orchestrator
│   ├── eval/                   # Evaluation & Guardrails engine
│   │   ├── __init__.py
│   │   ├── guardrails.py       # Pre-execution policy & PII sanitizer
│   │   └── evaluator.py        # LLM-as-a-Judge evaluation engine
│   └── verification/           # Continuous Verification & Benchmarking
│       ├── __init__.py
│       ├── metrics.py          # Benchmark metrics calculator
│       └── benchmark_runner.py # Regression test orchestrator & JSON reporter
└── tests/                      # Automated Pytest suite
    ├── __init__.py
    ├── test_llm_client.py      # Mission 1 validation
    ├── test_rag.py             # Mission 2 validation
    ├── test_agent.py           # Mission 3 validation
    ├── test_eval.py            # Mission 4 validation
    ├── test_verification.py    # Mission 5 validation
    ├── test_hybrid_search.py   # Mission 6 validation
    └── test_graph_orchestrator.py # Mission 7 validation
```

🛠️ Mission Progress
[x] Mission 1: Project Setup & Structured Inference Engine
  - Docker containerization for zero-dependency execution across environments.
  - Type-safe LLM client using Pydantic schema enforcement (StructuredLLMClient).
  - Unit tests with unittest.mock for fast, zero-cost CI/CD verification.

[x] Mission 2: In-Memory Vector Store & RAG Pipeline
  - Custom cosine similarity calculation & vector indexing (VectorStore).
  - Context-augmented response synthesis with source attribution (RAGPipeline).
  - Unit tests for similarity ranking and RAG orchestrator flow.

[x] Mission 3: Tool-Calling & Autonomous Agent Engine
  - ReAct-style Agent execution loop (AgentEngine).
  - Dynamic tool registry with safe mathematical evaluation (TOOL_REGISTRY).
  - Multi-step reasoning loop (Thought -> Action -> Observation -> Final Answer).
  - Pytest verification for tool execution and multi-step agent mocking.

[x] Mission 4: LLM Evaluation (LLM-as-a-Judge) & Guardrails (Upcoming)
  - Input security screening against prompt injection attacks (GuardrailEngine).
  - Automatic PII redaction for email addresses and telephone numbers.
  - LLM-as-a-Judge structured grading for output Faithfulness, Relevance, and Safety (LLMJudgeEvaluator).
  - Pytest verification for pre/post-execution policy enforcement and automated evaluation.

🗺️ Advanced LLM Engineering Roadmap
                       ┌────────────────────────────────────────┐
                       │      Solid Foundation Complete         │
                       │ (Structured Output, RAG, ReAct, Eval) │
                       └───────────────────┬────────────────────┘
                                           │
         ┌─────────────────────────────────┼─────────────────────────────────┐
         ▼                                 ▼                                 ▼
 1. Complex Agent Architectures     2. Advanced RAG & Retrieval     3. Model Adaptation & Ops
 - Multi-Agent Orchestration        - Hybrid Search (BM25 + Dense) - Parameter-Efficient Fine-Tuning
 - Cyclic Graphs (LangGraph)        - Re-ranking (Cross-Encoders)   - Model Distillation / Alignment
 - Stateful Memory & Persistence    - Agentic RAG / Dynamic Routing - Observability (LangSmith/Phoenix)

[x] Mission 5: Continuous Verification & Regression Benchmarking Engine (v1.1.0)
 - End-to-end benchmark dataset runner (ContinuousVerificationRunner).
 - Pass/fail score summary computation (calculate_summary).
 - Quantitative benchmark logging and JSON report export (benchmark_report.json).
 - Pytest verification for metric calculations and benchmark loop execution.

 [x] Mission 6: Hybrid Search Engine & Reciprocal Rank Fusion (v1.2.0)
 - Sparse lexical search engine using BM25 TF-IDF algorithm (BM25Retriever).
 - Reciprocal Rank Fusion (RRF) ranker blending dense vector search with lexical search (HybridSearchEngine).
 - Pytest verification for exact keyword matching, error code retrieval, and hybrid rank merging.

 [x] Mission 7: Multi-Agent State Graph Orchestrator (v1.3.0)
 - Shared workflow memory object tracking task state and history (AgentGraphState).
 - Node graph orchestrator supporting specialized agent role execution (MultiAgentGraphOrchestrator).
 - Conditional edge evaluation allowing multi-pass revision loops and explicit END transitions.
 - Maximum iteration safety guardrails to prevent infinite loop execution.

[x] Mission 8: Agentic RAG & Dynamic Query Decomposition (v1.4.0)
 - Query planner decomposing multi-faceted prompts into focused sub-queries (QueryPlan).
 - Independent sub-query execution across retrieval layers.
 - Multi-context aggregation and synthesized source-attributed response (AgenticRAGEngine).

🚀 Quick Start (Docker)
1. Set Environment Variables
Copy .env.example to .env and configure your API keys:

```bash
cp .env.example .env
```

2. Run Test Suite via Docker
Execute the full Pytest suite inside the isolated Docker container:

```bash
docker build -t llm-lab .
docker run --rm --env-file .env -v $(pwd):/app llm-lab
```
