# 🚀 Enterprise LLMOps & Autonomous Agent Kernel OS

A hands-on, test-driven repository for building production-grade LLM applications, RAG pipelines, and Autonomous Agent systems.

A production-grade, high-density Autonomous Agent Kernel & LLMOps Engine built from scratch using Python, Pydantic, and OpenTelemetry.

Every module in this repository is built with **strict type validation (Pydantic)**, **Docker containerization**, and **automated Pytest suites**.

  The unit test suite for PersistentMemoryEngine has been generated and validated. It uses Python's standard unittest framework to verify document management, cosine similarity, dense vector search, sparse BM25 search, RRF hybrid fusion, and dynamic memory pruning.

## 📂 Project Structure

```text
llm-engineering-lab/
├── Dockerfile                  # Containerized runtime for isolated execution
├── pyproject.toml              # Dependencies & Pytest configuration
├── requirements.txt            # Python package requirements
├── LICENSE                     # MIT License
├── ARCHITECTURE.md             # System architecture & data flow design
├── src/
│   ├── core/                         # Foundation LLM engine, security & optimization
│   │   ├── __init__.py
│   │   ├── llm_client.py             # Pydantic-enforced Structured LLM Client
│   │   └── distillation_pipeline.py  # Mission 17: Fine-Tuning & Model Distillation Pipeline
│   │   ├── kv_cache_manager.py       # Mission 21: High-Performance KV-Cache Manager
│   │   ├── llm_gateway.py            # Mission 24: Enterprise LLM Gateway & Rate Limiter
│   │   └── tenant_security_engine.py # Mission 28: Multi-Tenant Data Isolation & Security
│   │   └── lora_adapter_router.py    # Mission 29: Dynamic LoRA Adapter Router
│   │   └── speculative_prefetcher.py # Mission 41: Speculative Prompt Prefetching Engine
│   ├── rag/                    # Dense/Sparse Retrieval & RAG Orchestration
│   │   ├── __init__.py
│   │   ├── vector_store.py         # In-Memory Vector Store & Cosine Similarity engine
│   │   ├── rag_pipeline.py         # Context retrieval & synthesis orchestrator
│   │   ├── hybrid_search.py        # BM25 + Vector Search with Reciprocal Rank Fusion
│   │   ├── agentic_rag.py          # Mission 8: Agentic RAG Engine
│   │   ├── speculative_rag.py      # Mission 9: Speculative RAG Pipeline
│   │   ├── crag_pipeline.py        # Mission 10: Corrective RAG (CRAG) Engine
│   │   ├── self_rag.py             # Mission 11: Self-RAG (Self-Reflective Engine)
│   │   ├── adaptive_rag.py         # Mission 12: Adaptive RAG Router & Engine
│   │   └── multimodal_rag.py       # Mission 16: Multi-Modal RAG Engine & Visual Embedder
│   │   └── graph_rag.py            # Mission 18: GraphRAG & Knowledge Graph Entity-Relation Engine
│   │   └── persistent_memory.py    # Mission 26: Persistent Semantic Memory Engine
│   ├── graph/                    # Knowledge Graph Domain & GraphRAG Engines
│   │   ├── __init__.py
│   │   ├── graph_orchestrator.py     # Stateful Multi-Agent Graph Orchestrator (from agent/)
│   │   ├── graph_rag.py            # Mission 18: GraphRAG & Entity-Relation Engine (from rag/)
│   │   ├── graph_memory.py         # Persistent Knowledge Graph Memory Engine (from rag/)
│   │   └── federated_graph_mesh.py # Mission 40: Federated Knowledge Graph Mesh Engine
│   ├── agent/                  # Autonomous Tool-Calling & Speech/Vision Agents
│   │   ├── __init__.py
│   │   ├── tools.py                  # Tool registry & execution functions
│   │   ├── agent_engine.py           # ReAct-style Agent decision loop
│   │   ├── graph_orchestrator.py     # Mission 7: Stateful Graph Orchestrator
│   │   └── mcp_gateway.py            # Mission 14: MCP Tool Server & Protocol Gateway
│   │   └── audio_agent.py            # Mission 19: Real-Time Audio & Streaming Speech Agent
│   │   └── debate_orchestrator.py    # Mission 20: Multi-Agent Consensus & Debate Orchestrator
│   │   └── vision_document_agent.py  # Mission 23: Multi-Modal Vision Agent
│   ├── sandbox/                      # Code Execution Sandbox & Reflection Runtime
│   │   ├── __init__.py
│   │   ├── code_sandbox.py           # Mission 22: Autonomous Code Execution Sandbox
│   │   └── self_correction_engine.py # Mission 27: Self-Correction Sandbox & Code Feedback Loop
│   ├── eval/                   # Continuous Quality Evaluation & Guardrails
│   │   ├── __init__.py
│   │   ├── guardrails.py       # Pre-execution policy & PII sanitizer
│   │   ├── evaluator.py        # LLM-as-a-Judge evaluation engine
│   │   └── rag_benchmarker.py  # Mission 13: RAG Benchmark & Quality Evaluator
│   │   └── continuous_rag_evaluator.py # Mission 42: Continuous RAG Evaluation & Hallu Harness
│   ├── telemetry/              # Observability & Tracing
│   │   ├── __init__.py
│   │   └── telemetry_tracer.py     # Mission 25: OpenTelemetry Distributed Tracer
│   └── verification/           # Continuous Verification & Benchmarking
│       ├── __init__.py
│       ├── metrics.py          # Benchmark metrics calculator
│       └── benchmark_runner.py # Regression test orchestrator & JSON reporter
└── tests/                      # Automated Test Suite (1:1 paired with src)
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
    ├── test_graph_memory.py
    └── test_audio_agent.py      # Mission 19 validation
    └── test_debate_orchestrator.py # Mission 20 validation
    ├── test_kv_cache_manager.py       # Mission 21 validation
    ├── test_code_sandbox.py           # Mission 22 validation
    └── test_vision_document_agent.py# Mission 23 validation
    └── test_llm_gateway.py      # Mission 24 validation
    ├── test_telemetry_tracer.py       # Mission 25 validation
    ├── test_persistent_memory.py      # Mission 26 validation
    └── test_self_correction_engine.py # Mission 27 validation
    └── test_tenant_security_engine.py# Mission 28 validation
    └── tests/test_lora_adapter_router.py # Mission 30 validation
    ├── test_federated_graph_mesh.py


    ├── test_speculative_prefetcher.py    # Mission 41 validation
    └── test_continuous_rag_evaluator.py # Mission 42 validation
```

## 🎯 Mission Roadmap

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

- [x] **Mission 22: Autonomous Code Execution Sandbox (v2.8.0)**
  - Configurable security rules enforcing banned imports and prohibited function calls (`SecurityPolicy`).
  - AST-level static code auditing before execution without running untrusted code (`CodeSecurityAuditor`).
  - Isolated execution environment capturing stdout, stderr, return values, and policy violations (`CodeExecutionSandbox`).

- [x] **Mission 23: Multi-Modal Vision & Document Processing Agent (v2.9.0)**
  - Spatial document region-of-interest modeling with normalized bounding box bounds (`BoundingBox`, `DocumentLayoutElement`).
  - Structural layout visual parser segmenting headers, key-value pairs, tables, and images (`DocumentVisualParser`).
  - Multi-modal agent orchestrator performing grounded visual question answering and structured data extraction (`MultiModalVisionAgent`).

- [x] **Mission 24: Enterprise Multi-Tenant LLM Gateway & Rate Limiter (v3.0.0)**
  - Tenant context propagation and usage budget management (`TenantContext`, `UsageQuota`).
  - Sliding token bucket rate limiter enforcing Requests-Per-Minute (RPM) and Tokens-Per-Minute (TPM) caps (`TokenBucketRateLimiter`).
  - Enterprise proxy gateway with automated provider fallback and real-time monetary spend tracking (`EnterpriseLLMGateway`).

- [x] **Mission 25: Real-Time Telemetry, Tracing & Observability Pipeline (v3.1.0)**
  - Hierarchical execution span context propagation with parent-child trace tree generation (`ObservabilityTracer`).
  - Real-time LLM telemetry collection tracking token consumption, latency percentiles, and cost metrics (`LLMTelemetryCollector`).
  - Enterprise observability exporter generating trace span summaries and latency analytics (`TelemetrySummary`).

- [x] **Mission 26: Persistent Semantic Memory & Hybrid Retrieval Engine (v3.2.0)**
  - Vector space memory document schema with temporal metadata tracking (`MemoryDocument`, `SearchResult`).
  - Multi-retrieval engine fusing Dense Cosine Vector similarity and Sparse BM25 keyword matching via Reciprocal Rank Fusion (`PersistentMemoryEngine`).
  - Dynamic memory capacity management evicting stale contexts by timestamp retention policy (`prune_old_memories`).

- [x] **Mission 26 step2: consolidate Mission 18 GraphRAG and Mission 26 Persistent Memory into Dual Memory layer**
  - Property graph store with node properties and directed edgerelationships (`GraphRAGEngine`).
  - Multi-hop Breadth-First Search (BFS) neighborhood graph traversal and sub-graph extraction.
  - Automated entity-relation extraction from unstructured context streams.

- [x] **Mission 27: Self-Correction Sandbox & Code Feedback Loop (v3.3.0)**
  - Automated diagnostic feedback prompt generator capturing AST and runtime stack traces (`SelfCorrectionEngine`).
  - Iterative reflection loop orchestrating sandbox re-execution with candidate repairs (`CorrectionIteration`).
  - Graceful max-attempt fallback thresholds preventing infinite LLM execution loops (`execute_with_correction_loop`).

- [x] **Mission 28: Multi-Tenant Data Isolation & Security Policy Engine (v3.4.0)**
  - Tenant security policy schema and Role-Based Access Control (RBAC) validator (`TenantPolicy`, `SecurityContext`).
  - Row-Level Security (RLS) metadata filter generator for multi-tenant RAG retrieval isolation (`build_rls_filter`).
  - Tenant-scoped payload sanitization and tenant boundary enforcement engine (`MultiTenantIsolationEngine`).

- [x] **Mission 04/07: LLM Security & Guardrail Auditor (v1.2.0 / v1.5.0)**
  - Dual-pass security execution pipeline providing Input Prompt Sanitization and Output Payload Audit (`GuardrailAuditor`).
  - Regex & Named-Entity PII masking engine with bidirectional secure token substitution (`mask_pii`, `unmask_pii`).
  - System jailbreak / prompt injection classification and automated audit logging (`audit_log`).

- [x] **Mission 29: Dynamic Fine-Tuning & Adaptive LoRA Adapter Router (v3.5.0)**
  - Fine-tuned domain adapter metadata schema and registry pool (`LoRAAdapterConfig`, `DomainTaskType`).
  - Adaptive resolution selecting tenant-customized weights over shared enterprise domain adapters (`select_optimal_adapter`).
  - Zero-downtime weight hot-swapping execution engine on base LLM backbone (`hot_swap_adapter`).

- [x] **Mission 30: Multi-Modal RAG Document Parsing & Layout Analysis Engine (v3.6.0)**
  - Hierarchical Document AST parsing layout blocks with normalized 2D spatial bounding box coordinates (`BoundingBox`, `LayoutElement`).
  - Multi-Modal structural classification categorizing headers, paragraphs, tables, figures, and key-value grids (`ElementType`).
  - Specialized visual extraction pipeline isolating non-textual layout structures for visual vector indexing (`extract_tables_and_figures`).

- [x] **Mission 31: KV-Cache Multi-Modal Visual Context Retention Engine (v3.7.0)**
  - Visual token KV cache management engine preventing redundant image re-encoding across multi-turn sessions (`VisualKVCacheEngine`).
  - Memory-aware LRU eviction policy enforcing hardware token capacity budgets (`store_visual_tokens`, `_evict_lru_entry`).
  - Low-latency visual prefix cache retrieval with access metadata tracking (`get_visual_tokens`).

- [x] **Mission 32: Self-Healing Agent Circuit Breaker & Fallback Mesh (v3.8.0)**
  - State-machine driven circuit breaker protecting multi-agent loops from failure cascades (`AgentCircuitBreaker`, `CircuitState`).
  - Automated fallback routing for API timeouts and execution failures (`execute_with_fallback`).
  - Half-open recovery probes and consecutive failure threshold enforcement (`CircuitBreakerConfig`).

- [x] **Mission 33: Multi-Agent Consensus Graph & Conflict Resolution Engine (v3.9.0)**
  - Dynamic proposal aggregation and consensus resolution framework (`ConsensusGraphEngine`).
  - Support for multiple resolution strategies: weighted domain scoring, majority voting, and confidence thresholds (`ConsensusStrategy`).
  - Conflict arbitration among divergent multi-agent outputs (`resolve_consensus`).

- [x] **Mission 34: Enterprise Audit Logging, Compliance & Telemetry Mesh (v4.0.0)**
  - Cryptographically hashed, tamper-evident immutable audit logging chain (`AuditTelemetryMesh`, `AuditEvent`).
  - Strict verification of log chain integrity for SOC2/GDPR compliance auditing (`verify_chain_integrity`).
  - Tenant-isolated audit log filtering and severity classification (`get_tenant_audit_trail`, `AuditSeverity`).

- [x] **Mission 35: Real-Time Stream Evaluator & Hallucination Guard (v4.1.0)**
  - Token/chunk-by-chunk streaming response evaluation engine (`RealTimeStreamEvaluator`).
  - Early-stopping hallucination circuit breaker preventing ungrounded token delivery (`StreamChunkEvaluation`, `StreamSafetyStatus`).
  - Grounding validation against reference RAG context during live token streaming (`_compute_chunk_hallucination_score`).

  - [x] **Mission 36: Agentic Self-Healing Code Refactoring & AST Validation Sandbox (v4.2.0)**
  - Abstract Syntax Tree (AST) static analysis and syntax validation engine (`ASTRefactorSandboxEngine`).
  - Automatic AST transformer refactoring bare `except:` clauses and dangerous code constructs (`ASTSecurityAndCleanlinessTransformer`).
  - Code unparsing and structural integrity validation prior to sandbox execution (`validate_and_refactor`).

- [x] **Mission 37: Multi-Tenant Token Rate Limiter, Priority Scheduler & Cost Allocation Mesh (v4.3.0)**
  - Tiered SLA token bucket rate limiter supporting Enterprise, Pro, and Free tiers (`TenantPriorityScheduler`).
  - Priority-based queue arbitration level calculation (`get_tenant_priority`).
  - Micro-USD multi-tenant token consumption and cost allocation tracking (`record_cost_attribution`, `TenantCostMetrics`).

- [x] **Mission 38: Autonomous Agentic Tool-Use Registry & Schema Validator (v4.4.0)**
  - Dynamic agent tool registration and OpenAPI/JSON Schema metadata export (`AgentToolRegistry`).
  - Pre-execution argument schema validation for missing fields and type safety (`_validate_arguments`).
  - Safe function calling invocation and execution exception handling (`execute_tool`, `ToolExecutionResult`).

- [x] **Mission 39: Cross-Model Semantic Caching & Vector Similarity Deduplication Mesh (v4.5.0)**
  - Fast vector similarity lookup engine for zero-cost pre-computed LLM responses (`SemanticCacheEngine`).
  - Cosine similarity thresholding for semantically equivalent query deduplication (`_cosine_similarity`).
  - Multi-tenant isolated cache partition filtering (`CacheEntry`, `CacheHitResult`).

- [x] **Mission 40: Enterprise Federated Knowledge Graph & GraphRAG Entity Linking Mesh (v5.0.0)**
  - Multi-namespace federated graph node and edge representation (`FederatedKnowledgeGraphMesh`).
  - Breadth-First Search (BFS) multi-hop entity subgraph traversal (`extract_entity_subgraph`).
  - Namespace exploration tracking and context aggregation for GraphRAG (`SubgraphQueryResult`).

- [x] **Mission 41: Dynamic Speculative Prompt Prefetching & Context Cache Engine (v5.1.0)**
  - Dynamic intent association rules for multi-turn speculative context pre-warming (`SpeculativePromptPrefetcher`).
  - Pre-warmed context retrieval engine for turn-to-turn latency reduction (`predict_and_prefetch`, `get_prewarmed_context`).
  - Confidence-thresholded predictive pre-fetching (`PrefetchPrediction`).

- [x] **Mission 42: Continuous Automated RAG Evaluation & Hallucination Benchmark Harness (v5.2.0)**
  - Automated RAG triplet evaluation engine for Faithfulness, Relevance, and Recall (`ContinuousRAGEvaluatorEngine`).
  - Asynchronous hallucination flag thresholding and quality scoring (`RAGEvalMetrics`).
  - Automated quality drift telemetry generation for audit logging mesh integration.

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

