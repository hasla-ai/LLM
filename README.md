# 🚀 LLM Engineering Lab (`llm-engineering-lab`)

A hands-on, test-driven repository for building production-grade LLM applications, RAG pipelines, and Autonomous Agent systems.

Every module in this repository is built with **strict type validation (Pydantic)**, **Docker containerization**, and **automated Pytest suites**.

## 📂 Project Structure

```text
llm-engineering-lab/
├── Dockerfile                  # Containerized runtime for isolated execution
├── pyproject.toml              # Dependencies & Pytest configuration
├── requirements.txt            # Python package requirements
├── LICENSE                     # MIT License
├── ARCHITECTURE.md             # System architecture & data flow design
├── src/
│   ├── core/                   # Structured LLM inference engine & fine-tuning
│   │   ├── __init__.py
│   │   ├── llm_client.py       # Pydantic-enforced Structured LLM Client
│   │   └── distillation_pipeline.py # Mission 17: Fine-Tuning & Model Distillation Pipeline
│   ├── rag/                    # Retrieval-Augmented Generation engines
│   │   ├── __init__.py
│   │   ├── vector_store.py     # In-Memory Vector Store & Cosine Similarity engine
│   │   ├── rag_pipeline.py     # Context retrieval & synthesis orchestrator
│   │   ├── hybrid_search.py    # BM25 + Vector Search with Reciprocal Rank Fusion
│   │   ├── agentic_rag.py      # Mission 8: Agentic RAG Engine
│   │   ├── speculative_rag.py  # Mission 9: Speculative RAG Pipeline
│   │   ├── crag_pipeline.py    # Mission 10: Corrective RAG (CRAG) Engine
│   │   ├── self_rag.py         # Mission 11: Self-RAG (Self-Reflective Engine)
│   │   ├── adaptive_rag.py     # Mission 12: Adaptive RAG Router & Engine
│   │   └── multimodal_rag.py   # Mission 16: Multi-Modal RAG Engine & Visual Embedder
│   │   └── graph_rag.py        # Mission 18: GraphRAG & Knowledge Graph Entity-Relation Engine
│   ├── agent/                  # Autonomous Tool-Calling & Multi-Agent Graph
│   │   ├── __init__.py
│   │   ├── tools.py                # Tool registry & execution functions
│   │   ├── agent_engine.py         # ReAct-style Agent decision loop
│   │   ├── graph_orchestrator.py   # Mission 7: Stateful Graph Orchestrator
│   │   └── mcp_gateway.py          # Mission 14: MCP Tool Server & Protocol Gateway
│   │   └── audio_agent.py          # Mission 19: Real-Time Audio & Streaming Speech Agent
│   │   └── debate_orchestrator.py  # Mission 20: Multi-Agent Consensus & Debate Orchestrator
│   ├── eval/                   # Evaluation & Guardrails engine
│   │   ├── __init__.py
│   │   ├── guardrails.py       # Pre-execution policy & PII sanitizer
│   │   ├── evaluator.py        # LLM-as-a-Judge evaluation engine
│   │   └── rag_benchmarker.py  # Mission 13: RAG Benchmark & Quality Evaluator
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
    ├── test_graph_orchestrator.py # Mission 7 validation
    ├── test_agentic_rag.py      # Mission 8 validation
    ├── test_speculative_rag.py  # Mission 9 validation
    ├── test_crag_pipeline.py    # Mission 10 validation
    ├── test_self_rag.py         # Mission 11 validation
    ├── test_adaptive_rag.py     # Mission 12 validation
    ├── test_rag_benchmarker.py  # Mission 13 validation
    ├── test_mcp_gateway.py      # Mission 14 validation
    ├── test_adaptive_mcp_e2e.py  # Mission 15 validation
    ├── test_multimodal_rag.py   # Mission 16 validation
    └── test_distillation_pipeline.py # Mission 17 validation
    └── test_graph_rag.py        # Mission 18 validation
    └── test_audio_agent.py      # Mission 19 validation
    └── test_debate_orchestrator.py # Mission 20 validation
```

## 🎯 Mission Log & Architecture Roadmap

- **Mission 01:** Structured Outputs & Schema Enforcement (`StructuredLLMClient`, Pydantic validation)
- **Mission 02:** Hybrid RAG Pipeline (`DenseVectorStore`, BM25 sparse retrieval, Reciprocal Rank Fusion)
- **Mission 03:** Dynamic Prompt Engineering & Guardrails (`PromptTemplate`, input/output sanitization)
- **Mission 04:** Agentic Task Decomposition & Tool Calling (`TaskPlanner`, execution graph)
- **Mission 05:** Multimodal Data Processing & Embedding (`MultimodalEmbedder`, document vision)
- **Mission 06:** Memory Management & Context Compression (`ConversationMemory`, sliding window summary)
- **Mission 07:** LLM Security & Guardrail Auditor (`GuardrailAuditor`, PII masking, jailbreak defense)
- **Mission 08:** Corrective RAG (CRAG) with Web Fallback (`CorrectiveRAG`, dynamic web search fallback)
- **Mission 09:** Self-Reflective RAG (Self-RAG) (`SelfRAGEngine`, critique tokens, hallucination reflection)
- **Mission 10:** Speculative RAG Drafting (`SpeculativeRAGEngine`, dual-draft verification)
- **Mission 11:** Production Guardrails & Evaluation Engine (`LLMEvaluator`, toxicity & safety scoring)
- **Mission 12:** Adaptive RAG Engine (`AdaptiveRAGEngine`, upfront complexity routing)
- **Mission 13:** **Enterprise RAG Benchmarking & Automated Quality Evaluation Engine** (`RAGBenchmarker`, LLM-as-a-Judge quantitative quality profiling)
- **Mission 14:** Model Context Protocol (MCP) Gateway (MCPProtocolGateway, standard JSON-RPC tool server & capability management)
- **Mission 15:** **Adaptive RAG & MCP Integration Engine** (`E2EintegrationEngine`, multi-tier tool discovery & sandboxed JSON-RPC execution)
- **Mission 16**: Multi-Modal RAG Engine with Visual Embeddings (`MultimodalRAGEngine`, dual-modal vector index & visual document retrieval)
- **Mission 17**: Fine-Tuning & Model Distillation Pipeline (`DistillationTrainer`, dataset generation, quality filtering, and LoRA training)
- **Mission 18**: GraphRAG & Knowledge Graph Entity-Relation Engine (`GraphRAGEngine`, property graph store, multi-hop BFS neighborhood search, entity extraction)
- **Mission 19**: Real-Time Audio & Streaming Speech Agent (`RealTimeAudioAgent`, chunked audio frames, streaming TTS synthesis, voice turn orchestration)
- **Mission 20**: Multi-Agent Consensus & Debate Orchestrator (`MultiAgentDebateOrchestrator`, role-based agent debate, confidence-weighted consensus evaluation)
- **Mission 21**: Long-Context KV Cache Management System (`KVCacheManager`, `CacheEvictionPolicy`)
- **Mission 22**: Autonomous Code Execution Sandbox (`CodeExecutionSandbox`, `CodeSecurityAuditor`, `SecurityPolicy`)


**🛠️ Mission Progress**
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

[x] Mission 9: Speculative RAG & Draft-Verification Pipeline (v1.5.0)
 - Fast-path candidate answer generation via lightweight draft model (DraftAnswer).
 - High-capability verifier model scoring for accuracy and context compliance (VerificationResult).
 - Threshold-based acceptance or fallback correction (SpeculativeRAGPipeline).

[x] Mission 10: Corrective RAG (CRAG) & Adaptive Web Search Fallback (v1.6.0)
 - Self-correcting retrieval evaluator scoring document context quality (CRAGRetrieverEvaluator).
 - Dynamic grading (CORRECT, AMBIGUOUS, INCORRECT) and automated external search fallback trigger (CorrectiveRAGPipeline).

[x] Mission 11: Self-RAG Engine & Dynamic Reflection Tokens (v1.7.0)
 - Dynamic retrieval decision pre-check (RetrieveDecision) bypassing unnecessary search for direct/parametric questions.
 - Interleaved reflection token evaluation ([Retrieve], [IsREL], [IsSUP], [IsUSE]) assessing relevance, factual support, and response utility (SelfRAGEngine).
 - Fallback self-correction loop rewriting candidate answers when context support is degraded or hallucinated.

[x] Mission 12: Adaptive RAG Router & Multi-Tier Complexity Classification (v1.8.0)
 - Upfront prompt complexity analysis classifying queries into SIMPLE_NO_RAG, SINGLE_STEP_RAG, or COMPLEX_MULTI_STEP_RAG (ComplexityTier).
 - Dynamic execution routing optimizing latency, cost, and response quality across direct LLM, standard single-pass RAG, and agentic multi-pass pipelines (AdaptiveRAGEngine).

[x] Mission 13 introduces an automated, multi-dimensional evaluation suite designed to run quantitative benchmarking across standard, agentic, corrective, self-reflective, speculative, and adaptive RAG implementations.
- Quantitative multi-dimensional quality scoring engine using LLM-as-a-Judge (RAGBenchmarker).
- Context Faithfulness (Hallucination Score): Evaluates if generated assertions are strictly grounded in retrieved contexts without extrapolation.
- Answer Relevance: Measures directness and completeness in addressing the user prompt.
- Context Precision & Recall: Assesses signal-to-noise ratio in retrieved context passages.
- Latency Profiling: Tracks end-to-end multi-step execution timings per strategy.
- Consolidated report aggregator summarizing performance across RAG strategies (RAGBenchmarkReport).

[x] Mission 14: Model Context Protocol (MCP) Server & Tool Integration Gateway (v2.0.0)
- Standardized JSON-RPC 2.0 protocol handler (MCPProtocolGateway) for client-server capability exchange.
- Dynamic tool schema exposure and capability discovery (tools/list).
- Safe sandboxed execution of exposed tools (tools/call) with latency tracking and error handling (MCPExecutionResult).

- [x] **Mission 15: Adaptive RAG & MCP Protocol Integration Engine (v2.1.0)**
  - End-to-end integration between upfront prompt complexity routing and external tool protocols.
  - Automated MCP tool capability discovery (`tools/list`) triggered by `COMPLEX_MULTI_STEP_RAG` classification.
  - Sandboxed tool execution over JSON-RPC 2.0 protocol (`tools/call`) with error handling and latency tracking.

- [x] **Mission 16: Multi-Modal RAG Engine with Visual Embeddings (v2.2.0)**
  - Dual-modal embedder projecting textual passages and visual document scans into shared latent vector spaces (`MultimodalEmbedder`).
  - In-memory multi-modal vector store supporting modality filtering (TEXT, IMAGE, or hybrid) (`MultimodalVectorStore`).
  - Multi-modal RAG orchestrator synthesizing grounded responses with source attribution across text chunks and visual asset URIs (`MultimodalRAGEngine`).

- [x] **Mission 17: Fine-Tuning & Model Distillation Pipeline (v2.3.0)**
  - Synthetic dataset generation pipeline transforming raw text corpus into instruction-response pairs via Teacher LLM (`DistillationDatasetGenerator`).
  - Multi-stage quality filtering engine enforcing response confidence scores and minimum length criteria (`DatasetQualityFilter`).
  - Simulated LoRA/PEFT distillation trainer logging epoch loss convergence and generating fine-tuned model metadata (`DistillationTrainer`).

- [x] **Mission 18: GraphRAG & Knowledge Graph Entity-Relation Engine (v2.4.0)**
  - Entity and relationship extraction from unstructured textual content (`GraphExtractor`).
  - In-memory property graph store with dynamic entity nodes, directed relationship edges, and BFS multi-hop traversal (`KnowledgeGraphStore`).
  - Multi-hop subgraph expansion and grounded context generation engine (`GraphRAGEngine`).

- [x] **Mission 19: Real-Time Audio & Streaming Speech Agent (v2.5.0)**
  - Structured binary audio frame container supporting sample rates, frame IDs, and completion flags (`AudioFrame`).
  - Streaming Text-to-Speech (TTS) engine yielding real-time chunked audio frames from token streams (`StreamingTTS`).
  - Low-latency real-time voice interaction loop with simulated ASR, agent reasoning, and interruption state management (`RealTimeAudioAgent`).

- [x] **Mission 20: Multi-Agent Consensus & Debate Orchestrator (v2.6.0)**
  - Typed agent roles (PROPONENT, OPPONENT, JUDGE) and structured debate message containers (`DebateMessage`).
  - Multi-round debate orchestrator with dynamic confidence scoring and threshold-based consensus validation (`MultiAgentDebateOrchestrator`).
  - Auditable debate history tracking arguments, rebuttals, and final synthesized decisions (`ConsensusResult`).

- [x] **Mission 21: Long-Context Chunking & Dynamic KV Cache Manager (v2.7.0)**
  - Hierarchical document chunker with configurable token budgets and overlap alignment (`HierarchicalChunker`).
  - Simulated key-value (KV) attention cache block allocation and hit/miss metric collection (`DynamicKVCacheManager`).
  - Flexible memory eviction policies (`LRU` and `LFU`) to maintain strict context window caps under high query pressure.

- [x] **Mission 22: Autonomous Code Execution Sandbox**
  - Execute agent-generated Python code in a safe, controlled local environment with AST-based static analysis.

```bash
from src.agent.code_sandbox import CodeExecutionSandbox, SecurityPolicy

# 1. Initialize sandbox with default security boundaries
sandbox = CodeExecutionSandbox()

# 2. Execute safe python code snippet
safe_code = """
x = 10
y = 20
result = x + y
print(f"Computed total: {result}")
"""

res = sandbox.execute(safe_code)
print("Success:", res.is_success)
print("Stdout:", res.stdout)
print("Result Value:", res.return_value)

# 3. Execution of untrusted code is blocked statically
malicious_code = "import os; os.listdir('.')"
blocked_res = sandbox.execute(malicious_code)
print("Success:", blocked_res.is_success)
print("Violations:", blocked_res.violations)
```

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
