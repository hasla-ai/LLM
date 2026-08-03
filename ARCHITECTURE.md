# 🏛️ System Architecture

This document describes the architectural design and flow of the `llm-engineering-lab` system.

---

## 1. Core Principles

1. **Schema-First Integrity**
All LLM inputs, outputs, state objects, and evaluations are strictly bound to pydantic.BaseModel schemas. This guarantees deterministic, machine-readable JSON outputs and eliminates parsing errors at runtime.
2. **Environment Isolation & Reproducibility**
Docker serves as the primary runtime to bypass host OS constraints, guaranteeing cross-platform reproducibility across local, testing, and production environments.

3. **Test-Driven & Deterministic Evaluation**
System integrity is validated using automated Pytest suites backed by unittest.mock and LLM fixtures. This enables instant, zero-cost, and deterministic execution within CI/CD pipelines.

4. 5. **Continuous Quality Benchmarking**
Regressions in quality, safety, and relevance are systematically measured using structured benchmark suites.

5. **Adaptive Hybrid Retrieval Strategy**
The retrieval pipeline dynamically scales from standard dense semantic embeddings to hybrid search via Reciprocal Rank Fusion (RRF), sub-query decomposition (Agentic RAG), speculative drafting, self-correcting retrieval (CRAG), and self-reflective token grading (Self-RAG). —ensuring both conceptual understanding and exact-term precision.

6. **Cyclic & Resilient Multi-Agent Orchestration**
Workflows operate as stateful graphs with explicit node dependencies, conditional edges, and iteration safety bounds. Specialized agent nodes share a central state container across review and revision loops to enable resilient execution.
---

## 2. Module Architectures

## 🗺️ High-Level System Architecture


```text
                                            [ User / External Client Query ]
                                                            │
         1. ENTERPRISE GATEWAY & SECURITY PERIMETER         ▼
                                    ┌───────────────────────────────────────────────┐
                                    │ Enterprise Multi-Tenant Gateway & Rate Limiter│ (# 24)
                                    │  -> Token Bucket Rate Limiter                 │
                                    └───────────────────────┬───────────────────────┘
                                                            │
                                                            ▼
                                    ┌───────────────────────────────────────────────┐
                                    │ 🛡️ Multi-Tenant Data Isolation & Security     │ (# 28)
                                    │  -> RBAC, Clearance Levels & Namespace Filter │
                                    | MULTI-TENANT TOKEN RATE LIMITER               |
                                    | & COST ALLOCATION MESH                        |
                                    └───────────────────────┬───────────────────────┘
                                                            │
                                                            ▼
                                    ┌───────────────────────────────────────────────┐
                                    │ 🔒 LLM Security Guardrails - PASS 1 (INPUT)   │ (# 4/7)
                                    │  -> Prompt Injection Defense & PII Sanitizer  │
                                    └───────────────────────┬───────────────────────┘
                                                            │
                                                            ▼                                    
                                     ┌─────────────────────────────────────────────┐
                                     │ Enterprise Audit Logging Mesh Genesis Event │ (# 34)
                                     └──────────────────────┬──────────────────────┘
                                                            │
│  2. ADAPTIVE ROUTING & VISUAL INGESTION LAYER             ▼
                 ┌──────────────────────────────────────────┴────┐
                 │                                               │
                 ▼ (Visual / Image / Doc)                        ▼ (Text / Prompt Query)
┌─────────────────────────────────┐             ┌─────────────────────────────────┐
│ Multi-Modal Vision              │             │                                 │ 
| -> 👁️ Vision RAG Engine (#16)   |             |    Adaptive RAG Router (# 12)   │       
│ -> Document Agent (# 23)        |             |                                 |
    to Document Layout Analyzer (#30)           |                                 |
└────────────────┬────────────────┘               ───────────────┬────────────────┘
                 │                                               │          4. AGENTIC ORCHESTRATION & REASONING CORE(*)
                 |              ┌────────────────────────────────┼────────────────────────────────┐
                 │              │ (SIMPLE)                       │ (CODE_EXECUTION)               │ (COMPLEX)
                 │              ▼                                ▼                                ▼
                 │  ┌───────────────────────┐        ┌───────────────────────┐        ┌───────────────────────┐
                 │  │ Direct LLM Inference  │        │ Code Execution        │ (# 22) │ Multi-Agent Debate    │ (# 20)
                 │  │                       │        │ Sandbox Engine *      │        │ Engine *              │
                 │  └───────────┬───────────┘        └───────────┬───────────┘        └───────────┬───────────┘
                 │              │                                │                                │
                 │              │                                ▼                                │
                 │              │                    ┌───────────────────────┐                    │
                 │              │                    │ Self-Correction Loop *│ (# 27)             │
                 │              │                    └───────────┬───────────┘                    │
                 |              |                        ┌─────────────────────────────────────────────────-─┐           
                 |              |                        |            AST Refactor Sandbox (# 36)            |
                 |              |.                       └───────────┬───────────────────────────────────────┘
                 │              └────────────────────────────────────┼────────────────────────────┘
            ┌───────────────────────────────────────────────────────────────────┐
            |       SELF-HEAVY AGENT CIRCUIT BREAKER & FALLBACK MESH #32        |
            └───────────────────────────────────────────────────────────────────┘
                 │                                               │
                 │                                               ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Multi-Modal Visual                                │ Hierarchical Chunker & KV Cache (# 21)                  │
│  KV-Cache Retention Engine (#31)                  │                                                         │   
└─────────────────────────────────────────────────────────────────────────────────────────────-───────────────┘
                                                    │                │ Multi-Agent Debate
                                                    ▼                ▼      - Consensus* (#33)
                            ┌───────────────────────────────────────────────┐
                            │ ⚡ Dynamic LoRA Adapter Router        (# 29)   │
                            │  (Domain/Tenant Weight Hot-Swapping Engine)   │
                            └───────────────────────┬────────────────┬──────┘ 5. INFERENCE&RUNTIME OPTIMIZATION LAYER
                                                    │                │
 3. DUAL-TIER ISOLATED MEMORY & RETRIEVAL PIPELINE  ▼                ▼
                            ┌───────────────────────────────────────────────┐
                            │ Dual Memory & Retrieval Pipeline              │
                            │  ├─ 🧠 Persistent Semantic Memory (RRF) (# 26)│
                            │        ├─ Dense Vector Engine (Cosine Sim)    │
                            │        ├─ Sparse BM25 Engine (TF-IDF/IDF)     │
                            │        └─ Reciprocal Rank Fusion (RRF)        │
                            │  └─ GraphRAG Multi-Hop Graph Search  (# 18)   │
                            └───────────────────────┬────────────────┬──────┘
                                                    ▼                ▼                 
                            ┌───────────────────────────────────────────────┐         
                            │ Model Distillation Engine (# 17)              │         
                            │ (Synthetic LoRA Trainer)                      │
                            |  - Continuous learning flywheel -             |                            └───────────────────────┬────────────────┬──────┘
                                                    │                │        
6. STREAMING EVALUATION & GUARDRAILS PASS 2         ▼                ▼
                            ┌───────────────────────────────────────────────┐
                            │ 🔒 LLM Security Guardrails - PASS 2 (OUTPUT)   │ (# 4/7)
                            │  -> PII Unmasking, Output Policy & Audit Log  │
                            └───────────────────────┬───────────────────────┘
                                                    │
                                                    ▼
                            ┌───────────────────────────────────────────────┐
                            │ Real-Time Stream Evaluator                    │ (# 35)
                            │   & Hallucination Guard (# 35)                |
                            └───────────────────────┬───────────────────────┘                        
7. TELEMETRY, COMPLIANCE & CONTINUOUS LEARNING FLYWHEEL
                                                    ▼
                            ┌───────────────────────────────────────────────┐
                            │ 📊 Cryptographic Tamper-Evident               │ (# 34)
                            │   -> Audit Telemetry Mesh                     |
                            └───────────────────────┬───────────────────────┘

                            ┌───────────────────────────────────────────────┐
                            │ 📊 RAG Benchmarker Engine                     │ (# 13)
                            │ (Faithfulness, Relevancy & Evaluation)        │
                            └───────────────────────┬───────────────────────┘
                                                    │
                                                    ▼
                            ┌───────────────────────────────────────────────┐
                            │ 📡 OpenTelemetry Tracer & Distributed Spans   │ (# 25)
                            └───────────────────────────────────────────────┘
                                                    │
                                                    ▼
                                        [ Grounded Output ]
    ```
'시스템 구동 관점' - 호출 관계를 [어떤 레이어가 어떤 레이어를 포함/감싸고 있는가(Wrapping)]와 [데이터/요청이 들어오는 방향] 중 어디서 보느냐에 따라 로직의 시작점이 달라집니다.
[ 상위 / 바깥 레이어 : 라우팅 & 엔진 환경 준비 ]
┌─────────────────────────────────────────────────────────────┐
│  #29 LoRAAdapterRouter                                      │
│  - 요청의 성격(코드? 대화? 에이전트?)을 미리 감지                     │
│  - Base LLM에 필요한 LoRA 어댑터를 Hot-Swap으로 적재/바인딩          │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  [ 내부 / 실행 레이어 : 태스크 수행 ]                      │   │
│   │  #20 Multi-Agent / #22 Code Sandbox / Direct LLM    │   │
│   │  - 준비된 LoRA 환경(또는 라우터)을 거쳐 답변/코드 생성         │   │
│   └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
"진입점(Entry Point) 및 환경 설정 로직"
 - 요청 인터셉트 및 라우팅 (#29 우선 실행):
사용자의 요청이나 라우터 레이어로 전달된 메시지를 #29 LoRAAdapterRouter가 가장 먼저 받습니다.
 - LoRA Hot-Swap (바인딩):
#29가 "이 요청은 Python 코드를 작성/실행해야 하는 요청이군" 혹은 "Multi-Agent 조율용 태스크군"을 판별하고, Base LLM의 실행 컨텍스트에 해당 LoRA 어댑터를 무중단으로 미리 바인딩(Hot-Swap) 해둡니다.
 - 태스크 실행 (#20/#22 호출):
이미 올바른 어댑터가 꽂혀 있는 LLM 환경 위에서 #22 Code Sandbox가 코드를 생성하고 실행하거나, #20 Multi-Agent가 작동하여 결과를 만들어냅니다.

에이전트나 샌드박스가 "나 이제 모델 쓸게!" 하고 모델을 부르는 순간에 스위칭을 시작하면 지연 시간(Latency)이나 레이스 조건(Race Condition)이 생길 수 있습니다. 따라서 요청 진입 단계에서 #29가 에이전트/샌드박스가 일할 '무대(LoRA 어댑터)'를 먼저 셋업해 주는 흐름이 로직상 매우 자연스럽습니다.

"동적 의도 파악(Dynamic Agentic) 로직"
반대로 20/22 -> 29 흐름으로 설명되는 경우는 에이전트가 작동하는 도중에 '어떤 LoRA가 필요한지' 뒤늦게 결정되는 구조일 때입니다.
#20 Multi-Agent가 사용자의 복잡한 요구사항을 분석하기 시작합니다. 에이전트 루프 안에서 "아, 3단계 작업에서는 SQL 전용 LoRA가 필요하고, 4단계 작업에서는 C++ 코드 생성용 LoRA가 필요하네?" 라고 실행 중간에 판단합니다. 이 시점에 에이전트가 #29 LoRAAdapterRouter에게 "SQL 어댑터로 교체해 줘"라고 역호출(Call)하여 Hot-Swap을 수행합니다.

Inference Execution Subsystem 
┌────────────────────────────────────────────────────────────────────────┐
│               Inference Execution Subsystem                            │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │ 1. Request Scheduler & Batcher (PagedAttention Control)        │   │
│   └──────────────────────────────┬─────────────────────────────────┘   │
│                                  │                                     │
│   ┌──────────────────────────────▼─────────────────────────────────┐   │
│   │ 2. LoRA Adapter Manager (#29)                                  │   │
│   │    - Base Model Weights (Frozen, FP16/INT4)                    │   │
│   │    - Dynamic LoRA Weights (A, B Matrices)                      │   │
│   │    - Memory Pool (GPU HBM Segmented Manager)                   │   │
│   └──────────────────────────────┬─────────────────────────────────┘   │
│                                  │                                     │
│   ┌──────────────────────────────▼─────────────────────────────────┐   │
│   │ 3. Paged KV-Cache Engine (#21)                                 │   │
│   │    - Virtual Memory Blocks for Key/Value Tensors               │   │
│   └──────────────────────────────┬─────────────────────────────────┘   │
│                                  │                                     │
│   ┌──────────────────────────────▼─────────────────────────────────┐   │
│   │ 4. Compute Kernels (Triton / CUDA)                             │   │
│   │    - Custom BMM (Batch Matrix Multiplication) for LoRA         │   │
│   │    - FlashAttention-2 / PagedAttention Kernels                 │   │
│   └────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘


## 🧩 Core Subsystem Modules

## 1. Execution & Routing Tier
AdaptiveRAGEngine (src/rag/adaptive_rag.py): Upfront complexity classifier routing queries into fast-path direct generation, single-step RAG, or deep multi-pass agentic workflows.

SpeculativeRAGEngine (src/rag/speculative_rag.py): Parallel draft generation via lightweight models combined with speculative verification by larger primary LLMs.

CorrectiveRAGEngine (src/rag/corrective_rag.py): Retrieval evaluator trigger fallback web searches when local vector context quality drops below threshold.

SelfRAGEngine (src/rag/self_rag.py): Self-reflective critique loops inspecting retrieved passage utility and output hallucination rates.

## 2. Security & Guardrail Tier
GuardrailAuditor (src/eval/guardrails.py): Input sanitization, prompt injection detection, and outbound PII redactor.

## 3. Quantitative Evaluation Tier (Mission 13)
RAGBenchmarker (src/eval/rag_benchmarker.py): Enterprise evaluation engine delivering LLM-as-a-Judge multi-metric quality scores:
- Faithfulness (evaluate_faithfulness): Hallucination checking against context passages.
- Answer Relevance (evaluate_answer_relevance): Query addressing accuracy.
- Context Precision (evaluate_context_precision): Document signal-to-noise ratio.
- Report Aggregator (generate_report): Generates comparative benchmark summaries across strategies (StrategyBenchmarkSummary, RAGBenchmarkReport).

## 🔄 Quality Evaluation Execution Data Flow

[ Query + Answer + Contexts ]
                    │
                    ▼
          ┌───────────────────┐
          │  RAGBenchmarker   │
          └─────────┬─────────┘
                    │
   ┌────────────────┼────────────────┐
   │                │                │
   ▼                ▼                ▼
[Faithfulness]  [Relevance]     [Precision]
LLM-as-a-Judge  LLM-as-a-Judge  LLM-as-a-Judge
   │                │                │
   └────────────────┼────────────────┘
                    │
                    ▼
        [ RAGEvaluationResult ]
                    │
                    ▼
       [ RAGBenchmarkReport Summary ]
       

### Mission 1: Structured Inference Engine (`src/core/`)

ASCII Diagram

+------------------+         +--------------------------+         +----------------------+
|  User Request /  | ------> |   StructuredLLMClient    | ------> |    OpenAI API /      |
|  Prompt Input    |         |  (Pydantic Schema Guard) |         |  Structured Parse    |
+------------------+         +--------------------------+         +----------------------+
|                                  |
v Validate Output                  v Raw Response
+--------------------------+         +----------------------+
|   Validated Pydantic     | <------ |  Structured JSON     |
|   Python Object (T)      |         |  Object              |
+--------------------------+         +----------------------+

### Mission 2: Retrieval-Augmented Generation (`src/rag/`)

ASCII Diagram

+------------------+         +--------------------------+         +----------------------+
|  User Query +    | ------> |       VectorStore        | ------> | Top-K Ranked Context |
|  Query Embedding |         |  (Cosine Similarity)     |         | Chunks + Source IDs  |
+------------------+         +--------------------------+         +----------------------+
|
v
+------------------+         +--------------------------+         +----------------------+
|   RAGResponse    | <------ |   StructuredLLMClient    | <------ | Prompt Injection     |
| (Answer+Sources) |         |   (Context + Query)      |         | (Strict Context Rule)|
+------------------+         +--------------------------+         +----------------------+


### Mission 3: ReAct Agent & Tool-Calling Loop (`src/agent/`)

ASCII Diagram

                      +-------------------------+
                      |   User Prompt Input     |
                      +-------------------------+
                                   |
                                   v
                 +-----------------------------------+
                 |           AgentEngine             | <---------------------+
                 |      (Loop max_steps = N)         |                       |
                 +-----------------------------------+                       |
                                   |                                         |
                                   v                                         |
                 +-----------------------------------+                       |
                 |       StructuredLLMClient         |                       |
                 |      (Generates AgentAction)      |                       |
                 +-----------------------------------+                       |
                                   |                                         |
               +-------------------+-------------------+                     |
               |                                       |                     |
               v (if final_answer)                     v (if tool_name)      |
+-----------------------------+         +-----------------------------+      |
|    Return Final Answer      |         |     TOOL_REGISTRY Lookup    |      |
|    (Terminates Loop)        |         |  (e.g., calculator(input))  |      |
+-----------------------------+         +-----------------------------+      |
                                                       |                     |
                                                       v                     |
                                        +-----------------------------+      |
                                        |     Append Observation to   | -----+
                                        |     Conversation History    |
                                        +-----------------------------+

### Agent Action Schema (`AgentAction`)
* **`thought`** (`str`): Step-by-step reasoning process before action.
* **`tool_name`** (`Optional[str]`): Name of tool to execute (e.g., `"calculator"`) or `None`.
* **`tool_input`** (`Optional[str]`): Raw argument string passed to the targeted tool.
* **`final_answer`** (`Optional[str]`): Terminal response provided when task resolution is complete.      

### Mission 4: Guardrails & LLM-as-a-Judge Evaluation (`src/eval/`)

                   +-----------------------------+
                   |      Raw User Input         |
                   +-----------------------------+
                                  |
                                  v
                   +-----------------------------+
                   |      GuardrailEngine        |
                   | (Injection & PII Screening) |
                   +-----------------------------+
                       /                     \
             (Unsafe) /                       \ (Safe / PII Sanitized)
                     v                         v
      +-----------------------------+   +-----------------------------+
      |  Reject Request / Return    |   |    Core LLM / RAG / Agent   |
      |  GuardrailViolation Exception |   |         Execution           |
      +-----------------------------+   +-----------------------------+
                                                       |
                                                       v
                                        +-----------------------------+
                                        |     LLMJudgeEvaluator       |
                                        |  (Structured Output Score)  |
                                        +-----------------------------+
                                                       |
                                                       v
                                        +-----------------------------+
                                        |      EvaluationScore        |
                                        |  - Faithfulness (1-5)       |
                                        |  - Relevance (1-5)          |
                                        |  - Safety (1-5)             |
                                        |  - Reasoning Explanation    |
                                        +-----------------------------+

### Evaluation Schema (`EvaluationScore`)
* **`faithfulness`** (`int`, range 1-5): Verifies whether generated claims are strictly grounded in retrieved context.
* **`relevance`** (`int`, range 1-5): Assesses how directly the output addresses the original user prompt.
* **`safety`** (`int`, range 1-5): Checks output for compliance with content policies and ethical guidelines.
* **`reasoning`** (`str`): Provides explicit justification for the numerical scores assigned.


### Mission 5: Continuous Verification Engine (`src/verification/`)

+-----------------------------------+
|     Benchmark Dataset (JSON/List) |
| [query, context, expected_answer] |
+-----------------------------------+
|
v
+-----------------------------------+
|   ContinuousVerificationRunner    |
| (Iterates entries over pipelines) |
+-----------------------------------+
|
+--------+--------+
|                 |
v                 v
+-----------------+ +--------------------+
| GuardrailEngine | | LLMJudgeEvaluator  |
| (Safety check)  | | (Quality scoring)  |
+-----------------+ +--------------------+
|                 |
+--------+--------+
|
v
+-----------------------------------+
|      metrics.calculate_summary    |
| - safe_pass_rate (%)              |
| - avg_faithfulness (1.0-5.0)      |
| - avg_relevance (1.0-5.0)         |
| - passed_all_criteria (Bool)      |
+-----------------------------------+
|
v
+-----------------------------------+
|      benchmark_report.json        |
|  (Exported artifacts for CI/CD)   |
+-----------------------------------+

### Verification Metrics Schema (`VerificationSummary`)
* **`total_queries`** (`int`): Count of benchmark items processed.
* **`safe_pass_rate`** (`float`): Percentage of requests that passed input/output safety policy checks.
* **`avg_faithfulness`** (`float`): Mean faithfulness score across all items (scale 1.0 - 5.0).
* **`avg_relevance`** (`float`): Mean relevance score across all items (scale 1.0 - 5.0).
* **`passed_all_criteria`** (`bool`): Evaluates `True` only when `safe_pass_rate == 100.0%`, `avg_faithfulness >= 4.0`, and `avg_relevance >= 4.0`.


-------
### Mission 6: Hybrid Search & Reciprocal Rank Fusion (`src/rag/hybrid_search.py`)
- "The following ASCII diagram needs to be validated."
                    +------------------------------------+
                    |      User Query + Embedding        |
                    +------------------------------------+
                             |                  |
             +---------------+                  +---------------+
             |                                                  |
             v                                                  v
    +---------------------------+                      +---------------------------+
    |   Dense Vector Search     |                      |    Sparse Lexical Search  |
    | (Cosine Distance Ranking) |                      |     (BM25 TF-IDF Engine)  |
    +---------------------------+                      +---------------------------+
                |                                                  |
                | Dense Ranks                              Sparse  | Ranks
                +---------------+                  +---------------+
                                |                  |
                                v                  v
                +------------------------------------+
                |    Reciprocal Rank Fusion (RRF)    |
                | RRF = 1/(k + Rank_v) + 1/(k + Rank_b)|
                +------------------------------------+
                                |
                                v
                +------------------------------------+
                |    Unified Top-K Ranked Context    |
                |      (High Keyword + Semantic)     |
                +------------------------------------+

### Reciprocal Rank Fusion Formula
$$RRF\_Score(d \in D) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$
* $M$: Set of retrievers (Dense Vector & BM25 Sparse Lexical).
* $r_m(d)$: Rank position of document $d$ in retriever $m$ (1-indexed).
* $k$: Constant smoothing parameter (default $k = 60$).

### Mission 7: Stateful Multi-Agent Graph Orchestrator (`src/agent/graph_orchestrator.py`)

The `MultiAgentGraphOrchestrator` replaces strict sequential execution with a directed graph model where node functions manipulate a unified state container (`AgentGraphState`). Edges between nodes can be unconditional or conditional, enabling dynamic decision-making and cyclic write-review loops.

                  +-----------------------------------+
                  |      AgentGraphState (Initial)    |
                  |   - task                          |
                  |   - step_count = 0                |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |          ResearcherNode           |
                  |   (Gathers background facts)      |
                  +-----------------------------------+
                                    |
                                    v
+---------------------------------------------------------------------------------+
|                                                                                 |
|                     +-----------------------------------+                       |
|  +----------------> |            WriterNode             |                       |
|  |                  |   (Drafts or revises content)     |                       |
|  |                  +-----------------------------------+                       |
|  |                                    |                                         |
|  |                                    v                                         |
|  |                  +-----------------------------------+                       |
|  |                  |           ReviewerNode            |                       |
|  |                  |   (Evaluates draft quality)       |                       |
|  |                  +-----------------------------------+                       |
|  |                                    |                                         |
|  |                                    v                                         |
|  |                  +-----------------------------------+                       |
|  |                  |         Conditional Edge          |                       |
|  |                  |    review_condition(state)        |                       |
|  |                  +-----------------------------------+                       |
|  |                                 /     \                                      |
|  |        (is_approved == False)  /       \  (is_approved == True OR            |
|  +-------------------------------+         \  step_count >= max_steps)          |
|                                             v                                   |
|                                  +--------------------+                         |
|                                  |        END         |                         |
|                                  +--------------------+                         |
+---------------------------------------------------------------------------------+

#### Core Components
1. **`AgentGraphState`**: Immutable state model passed through node transitions. Accumulates outputs (`research_notes`, `draft_content`, `review_feedback`) and tracks operational metrics (`step_count`, `history`).
2. **`GraphNode`**: Wrapper standardizing node execution, automatically logging history and enforcing step counters.
3. **`MultiAgentGraphOrchestrator`**: Graph runtime that registers nodes, static edges (`add_edge`), and dynamic routing functions (`add_conditional_edge`).

### Mission 8: Agentic RAG & Query Decomposition (`v1.4.0`)

                    +----------------------------------+
                    |       Complex User Prompt        |
                    +----------------------------------+
                                     |
                                     v
                    +----------------------------------+
                    |      Query Planner (LLM)         |
                    | Decomposes into Sub-Queries 1..N |
                    +----------------------------------+
                                     |
             +-----------------------+-----------------------+
             |                                               |
             v                                               v
+-----------------------------+                 +-----------------------------+
|  Sub-Query 1 Execution      |                 |  Sub-Query 2 Execution      |
|  (Vector/Hybrid Search)     |                 |  (Vector/Hybrid Search)     |
+-----------------------------+                 +-----------------------------+
            |                                               |
            +-----------------------+-----------------------+
                                    |
                                    v
                    +----------------------------------+
                    |  Context Aggregator & Deduper    |
                    +----------------------------------+
                                    |
                                    v
                    +----------------------------------+
                    |  Synthesis Orchestrator (LLM)    |
                    | Returns AgenticRAGResponse       |
                    +----------------------------------+

### Mission 9: Speculative RAG Pipeline (`v1.5.0`)
                    +----------------------------------+
                    |       User Query + Context       |
                    +----------------------------------+
                                     |
                                     v
                    +----------------------------------+
                    |  Fast Draft Model (Lightweight)  |
                    |    Generates Candidate Draft     |
                    +----------------------------------+
                                     |
                                     v
                    +----------------------------------+
                    |    Verifier Model (Heavy LLM)    |
                    |   Scores Draft & Factuality      |
                    +----------------------------------+
                                /          \
        (Score >= Threshold)   /            \   (Score < Threshold)
                              v              v
                 +--------------------+     +---------------------+
                 | Accept Draft Text  |     | Corrected Verifier  |
                 |  (Fast Response)   |     | Answer (Safe Fall)  |
                 +--------------------+     +---------------------+
                              \              /
                               v            v
                    +----------------------------------+
                    |      SpeculativeRAGResponse      |
                    +----------------------------------+

### Mission 10: Corrective RAG (CRAG) Engine (`src/rag/crag_pipeline.py`)

                    +----------------------------------+
                    |       User Query Prompt          |
                    +----------------------------------+
                                     |
                                     v
                    +----------------------------------+
                    |   Local Vector Retrieval Pass    |
                    +----------------------------------+
                                     |
                                     v
                    +----------------------------------+
                    |   Retrieval Quality Evaluator    |
                    |   Assigns Grade & Confidence     |
                    +----------------------------------+
                               /     |     \
                  +-----------+      |      +-----------+
                  |                  |                  |
                  v                  v                  v
             [CORRECT]          [AMBIGUOUS]        [INCORRECT]
                  |                  |                  |
                  v                  v                  v
         +------------------+ +--------------+  +-----------------+
         | Use Local Docs   | | Augment with |  | Discard Local   |
         | Directly         | | Web Search   |  | Use Web Search  |
         +------------------+ +--------------+  +-----------------+
                  \                  |                  /
                   +-----------------+-----------------+
                                     |
                                     v
                    +----------------------------------+
                    |  Context Synthesis Orchestrator  |
                    |     Returns CRAGResponse         |
                    +----------------------------------+

### Mission 11: Self-RAG Engine (`src/rag/self_rag.py`)

                    +----------------------------------+
                    |       User Query Prompt          |
                    +----------------------------------+
                                     |
                                     v
                    +----------------------------------+
                    |   Retrieval Pre-Check Evaluator  |
                    |    [Retrieve]: YES vs NO         |
                    +----------------------------------+
                                /          \
                 (Retrieve=YES)/            \(Retrieve=NO)
                              v              v
           +----------------------+      +----------------------+
           | Vector Retrieval     |      | Direct Generator     |
           | Candidate Generator  |      | Parametric Memory    |
           +----------------------+      +----------------------+
                      \                      /
                       \                    /
                        v                  v
                    +----------------------------------+
                    |  Interleaved Reflection Evaluator|
                    |  - Passage Relevance ([IsREL])   |
                    |  - Context Support   ([IsSUP])   |
                    |  - Answer Utility    ([IsUSE])   |
                    +----------------------------------+
                                     |
                                     v
                    +----------------------------------+
                    |  Self-Correction Trigger Check   |
                    | (If UNSUPPORTED -> Fallback Loop)|
                    +----------------------------------+
                                     |
                                     v
                    +----------------------------------+
                    |         SelfRAGResponse          |
                    +----------------------------------+

### Mission 12: Adaptive RAG Engine (`src/rag/adaptive_rag.py`)                    
                    +----------------------------------+
                    |       Incoming User Prompt       |
                    +----------------------------------+
                                     |
                                     v
                    +----------------------------------+
                    |   Query Complexity Classifier    |
                    |    (RoutingDecision Router)      |
                    +----------------------------------+
                              /      |      \
                             /       |       \
                            v        v        v
     +------------------------+  +-------+  +------------------------+
     |     SIMPLE_NO_RAG      |  |SINGLE_|  | COMPLEX_MULTI_STEP_RAG |
     | (Parametric/Direct)    |  | STEP_ |  |  (Agentic Decomposition|
     +------------------------+  |  RAG  |  |   & Sub-Query Loop)    |
                 |               +-------+  +------------------------+
                 |                   |                   |
                 v                   v                   v
     +------------------------+  +-------+  +------------------------+
     | Direct Structured LLM  |  |Standard| | AgenticRAGEngine Pass  |
     | Prompt Execution       |  | RAG   |  | Multi-Pass Execution   |
     +------------------------+  +-------+  +------------------------+
                 \                   |                   /
                  +------------------+------------------+
                                     |
                                     v
                    +----------------------------------+
                    |       AdaptiveRAGResponse        |
                    +----------------------------------+

### MISSION 13: ENTERPRISE RAG BENCHMARKING & EVALUATION ENGINE (`src/eval/rag_benchmarker.py`)

[ Evaluation Input ]
   ├── Query: str
   ├── Answer: str
   ├── Contexts: List[str]
   └── Latency: float
          │
          ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            RAGBenchmarker Engine                             │
│                      (src/eval/rag_benchmarker.py)                           │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│ Faithfulness    │     │ Answer          │     │ Context          │
│ Evaluator       │     │ Relevance       │     │ Precision        │
│ (Hallucination) │     │ Evaluator       │     │ Evaluator        │
└────────┬────────┘     └────────┬────────┘     └────────┬─────────┘
         │                       │                       │
         │ Structured Output     │ Structured Output     │ Structured Output
         │ (Score 0.0-1.0)       │ (Score 0.0-1.0)       │ (Score 0.0-1.0)
         ▼                       ▼                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            RAGEvaluationResult                               │
│  - faithfulness_score, answer_relevance_score, context_precision_score       │
│  - latency_seconds, reasoning_trace, timestamp                               │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            RAGBenchmarkReport                                │
│    - Multi-Strategy Comparison Summaries                                     │
│    - Aggregated Quality Averages & Latency Distributions                     │
└──────────────────────────────────────────────────────────────────────────────┘

#### Pydantic Schemas

```bash
from pydantic import BaseModel, Field
from typing import List, Optional

class MetricEvaluation(BaseModel):
    """Structured response for an individual quality metric evaluation."""
    score: float = Field(..., ge=0.0, le=1.0, description="Normalized metric score between 0.0 and 1.0")
    reasoning: str = Field(..., description="LLM-as-a-Judge chain-of-thought justification")

class RAGEvaluationResult(BaseModel):
    """Aggregated multi-metric assessment for a single RAG inference execution."""
    query: str
    generated_answer: str
    retrieved_contexts: List[str]
    faithfulness: MetricEvaluation
    answer_relevance: MetricEvaluation
    context_precision: MetricEvaluation
    latency_seconds: float

class StrategyBenchmarkSummary(BaseModel):
    """Aggregated quantitative performance summary across a specific RAG strategy."""
    strategy_name: str
    total_samples: int
    avg_faithfulness: float
    avg_answer_relevance: float
    avg_context_precision: float
    avg_latency_seconds: float

class RAGBenchmarkReport(BaseModel):
    """Full enterprise benchmark report comparing multiple RAG architectural strategies."""
    summaries: List[StrategyBenchmarkSummary]
    recommended_strategy: str
```
### MISSION 14: MODEL CONTEXT PROTOCOL (MCP) GATEWAY ARCHITECTURE(`src/agent/mcp_gateway.py`)

[ Client / Agent Request ]
            │
            ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                             MCPProtocolGateway                               │
│                         (src/agent/mcp_gateway.py)                           │
│  - Handshake / Capability Exchange (JSON-RPC 2.0)                            │
│  - Dynamic Tool Registration & Discovery                                     │
│  - Secure Execution Sandbox & Parameter Validation                           │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ MCP Resource     │    │ MCP Tool         │    │ MCP Prompt       │
│ Provider         │    │ Execution        │    │ Template         │
│ (System State)   │    │ (Sandbox Tools)  │    │ (Context Ingest) │
└────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                             MCPExecutionResult                               │
│  - status: "success" | "error" | "denied"                                    │
│  - result_payload / error_message                                            │
│  - execution_latency_ms                                                      │
└──────────────────────────────────────────────────────────────────────────────┘

**Core Subsystem Schemas**
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class MCPCapability(str, Enum):
    RESOURCES = "resources"
    TOOLS = "tools"
    PROMPTS = "prompts"

class MCPToolSchema(BaseModel):
    """Schema defining an MCP-compliant tool exposure."""
    name: str = Field(..., description="Unique tool identifier")
    description: str = Field(..., description="Description of the tool function")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema for parameters")

class MCPRequest(BaseModel):
    """JSON-RPC 2.0 compliant MCP Protocol Request."""
    jsonrpc: str = Field(default="2.0")
    id: str = Field(..., description="Unique request ID")
    method: str = Field(..., description="MCP Protocol method (e.g. tools/list, tools/call)")
    params: Dict[str, Any] = Field(default_factory=dict)

class MCPExecutionResult(BaseModel):
    """Structured response payload for MCP executions."""
    request_id: str
    status: str = Field(..., description="'success', 'error', or 'denied'")
    content: Optional[Any] = None
    error_message: Optional[str] = None
    execution_latency_ms: float

### MISSION 15: E2E INTEGRATION: ADAPTIVE RAG + MCP PROTOCOL GATEWAY (`tests/test_e2e_adaptive_mcp.py`)
                                [ User Query ]
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │    AdaptiveRAGEngine     │ (Mission 12)
                         │ (Upfront Router/Planner) │
                         └────────────┬─────────────┘
                                      │
           ┌──────────────────────────┼──────────────────────────┐
           │ (SIMPLE)                 │ (SINGLE_STEP)            │ (COMPLEX)
           ▼                          ▼                          ▼
┌────────────────────┐      ┌──────────────────┐       ┌──────────────────┐
│  Direct Answer     │      │ Standard Vector  │       │ MCP Tool Gateway │ (Mission 14)
│  (No Retrieval)    │      │ Pipeline         │       │ (JSON-RPC 2.0)   │
└────────────────────┘      └──────────────────┘       └────────┬─────────┘
                                                                │
                                                ┌───────────────┴───────────────┐
                                                ▼                               ▼
                                     ┌─────────────────────┐         ┌─────────────────────┐
                                     │  `tools/list`       │         │  `tools/call`       │
                                     │ Schema Discovery    │         │ Sandboxed Execution │
                                     └─────────────────────┘         └─────────────────────┘

### MISSION 16: MULTI-MODAL RAG ENGINE ARCHITECTURE (`src/rag/multimodal_rag.py`)

================================================================================
           MISSION 16: MULTI-MODAL RAG ENGINE ARCHITECTURE
================================================================================

                [ Query: Text + Optional Image Input ]
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            MultimodalEmbedder                                │
│                     (src/rag/multimodal_rag.py)                              │
│  - Generates aligned embeddings for text & visual assets                     │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         MultimodalVectorStore                                │
│  - Dense Index supporting text & visual document assets                      │
│  - Cosine similarity ranking across modality filters ('text', 'image', 'all') │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                          MultimodalRAGEngine                                 │
│  - Aggregates text context passages & visual asset URIs                      │
│  - Synthesizes grounded answers with source attribution & visual references │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
                                 ▼
                       [ MultimodalRAGResponse ]

**Core Subsystem Schemas**
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ModalityType(str, Enum):
    TEXT = "text"
    IMAGE = "image"

class MultimodalDocument(BaseModel):
    """Container for multi-modal document chunks (text or visual assets)."""

### MISSION 17: MODEL DISTILLATION & FINE-TUNING PIPELINE (`src/rag/multimodal_rag.py`)

[ Unstructured Corpus / Raw Context ]
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│              DistillationDatasetGenerator                │
│       (Teacher Model Prompting & Dataset Structuring)    │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│                 DatasetQualityFilter                     │
│    (Teacher Confidence, Length, & Sanity Checking)      │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼ [ High-Quality Dataset ]
┌──────────────────────────────────────────────────────────┐
│                   DistillationTrainer                    │
│   (Simulated LoRA/PEFT Training & Epoch Loss Tracking)   │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
       [ Fine-Tuned Model Checkpoint ]

┌────────────────────────────────────────────────────────────────────────┐
 │                      REAL-TIME REQUEST PIPELINE                        │
 │                                                                        │
 │  User Request ──► Pass 1 ──► Memory (#18/#26) ──► Multi-Agent (#20)    │
 │                                                         │              │
 │                                                         ▼              │
 │  Final Output ◄── Pass 2 ◄── ConsensusGraph (#33) ◄── [ High-Quality   │
 │                                                         Proposals ]    │
 └────────────────────────────────────┬───────────────────────────────────┘
                                      │
                                      ▼ (Asynchronous Data Logging)
 ┌────────────────────────────────────────────────────────────────────────┐
 │                   OFFLINE CONTINUOUS LEARNING FLYWHEEL                 │
 │                                                                        │
 │                     [ High-Quality Telemetry Logs ]                    │
 │                                    │                                   │
 │                                    ▼                                   │
 │                    Model Distillation Engine (#17)                     │
 │               (Extracts synthetic training pairs & distill)            │
 │                                    │                                   │
 │                                    ▼                                   │
 │                   [ New Fine-Tuned LoRA Adapter ]                      │
 │                                    │                                   │
 │                                    ▼                                   │
 │                  Dynamic LoRA Adapter Router (#29)                     │
 │                  (Hot-swaps new weights into live LLM)                 │
 └────────────────────────────────────────────────────────────────────────┘

**Core Subsystem Schemas**
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class DistillationSample(BaseModel):
    """Container for a single synthetic instruction-response sample generated by teacher."""
    instruction: str
    teacher_response: str
    quality_score: float = Field(..., ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TrainingConfig(BaseModel):
    """Configuration for model distillation and fine-tuning."""
    student_model_name: str = "student-small-7b"
    epochs: int = 3
    learning_rate: float = 2e-4
    lora_rank: int = 8

class TrainingMetrics(BaseModel):
    """Metrics recorded during model distillation training."""
    epoch_losses: List[float]
    final_loss: float
    status: str

### MISSION 18: GRAPHRAG ENTITY-RELATION ENGINE (`src/rag/graph_rag.py`)

[ Unstructured Document / Text Chunk ]
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│                     GraphExtractor                       │
│     (Extracts Nodes: Entities, Edges: Relations)         │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│                   KnowledgeGraphStore                    │
│   (Adjacency Index, Multi-Hop Neighbor Traversal)        │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│                     GraphRAGEngine                       │
│  (Combines Subgraph Expansion with Grounded Synthesis)   │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
            [ GraphRAGResponse ]

**Core Subsystem Schemas**
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class Entity(BaseModel):
    """Node representing a real-world entity in the Knowledge Graph."""
    id: str
    type: str
    description: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Relationship(BaseModel):
    """Directed edge representing a relationship between two entities."""
    source_id: str
    target_id: str
    relation_type: str
    description: str = ""
    weight: float = 1.0

class GraphRAGResponse(BaseModel):
    """Response output from GraphRAG multi-hop retrieval and synthesis."""
    query: str
    answer: str
    retrieved_entities: List[str]
    retrieved_relations: List[str]
    subgraph_depth: int

Refer to Mission 26 for 'MISSION 18 & 26: DUAL-TIER KNOWLEDGE & SEMANTIC RETRIEVAL PIPELINE'.

### MISSION 19: REAL-TIME AUDIO & STREAMING SPEECH AGENT (`src/rag/audio_agent.py`)

[ User Speech / Audio Stream ]
                    │
                    ▼
┌──────────────────────────────────────────────────────────┐
│                   AudioFrame Ingestion                   │
│         (PCM / Byte Chunk Processing & Sequence)         │
└───────────────────┬──────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────────┐
│                   RealTimeAudioAgent                     │
│         (Context Tracking & Interruption State)          │
└───────────────────┬──────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────────┐
│                      StreamingTTS                        │
│        (Text Chunk -> Audio Stream Synthesis)            │
└───────────────────┬──────────────────────────────────────┘
                    │
                    ▼
       [ Streaming Audio Output Frames ]

## Core Subsystem Schemas ##

from typing import Any, List, Optional
from pydantic import BaseModel, Field

class AudioFrame(BaseModel):
    """Container for streaming audio chunks."""
    frame_id: int
    data: bytes
    sample_rate: int = 16000
    format: str = "pcm"
    is_final: bool = False

class AudioAgentResponse(BaseModel):
    """Response returned by the audio agent loop."""
    transcript: str
    response_text: str
    audio_frames: List[AudioFrame]
    interrupted: bool = False

### MISSION 20: MULTI-AGENT CONSENSUS & DEBATE ORCHESTRATOR (`src/agent/debate_orchestrator.py`)

================================================================================
          MISSION 20: MULTI-AGENT CONSENSUS & DEBATE ORCHESTRATOR
================================================================================

                         [ Debate Topic / Task ]
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                        MultiAgentDebateOrchestrator                          │
│                                                                              │
│   ┌────────────────────┐    Round N     ┌────────────────────┐              │
│   │  Proponent Agent   │ ───────────────► │   Opponent Agent   │              │
│   └─────────┬──────────┘                └─────────┬──────────┘              │
│             │                                     │                          │
│             └──────────────────┬──────────────────┘                          │
│                                │ (Arguments)                                 │
│                                ▼                                             │
│                   ┌──────────────────────────┐                               │
│                   │      Judge / Moderator   │                               │
│                   └────────────┬─────────────┘                               │
└────────────────────────────────┼─────────────────────────────────────────────┘
                                 │
                                 ▼
                    [ Consensus Result & Decision ]

**Core Subsystem Schemas**
from enum import Enum
from typing import List
from pydantic import BaseModel, Field

class AgentRole(str, Enum):
    PROPONENT = "PROPONENT"
    OPPONENT = "OPPONENT"
    JUDGE = "JUDGE"

class DebateMessage(BaseModel):
    """Container for a single argument or rebuttal turn in a debate."""
    speaker_role: AgentRole
    speaker_name: str
    content: str
    confidence: float = Field(..., ge=0.0, le=1.0)

class ConsensusResult(BaseModel):
    """Final decision output synthesized from multi-agent debate."""
    topic: str
    decision: str
    confidence_score: float
    total_rounds: int
    consensus_reached: bool

### MISSION 21: LONG-CONTEXT CHUNKING & DYNAMIC KV CACHE MANAGER (`src/core/context_cache.py`)

================================================================================
       MISSION 21: LONG-CONTEXT CHUNKING & DYNAMIC KV CACHE MANAGER
================================================================================

                  [ Long Document / Extended Prompt Stream ]
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            Hierarchical Chunking                             │
│         (Token Budget Partitioning & Overlap Window Alignment)               │
└────────────────────────────────────┬─────────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                           DynamicKVCacheManager                              │
│                                                                              │
│  ┌────────────────────────┐  Prefix Hit  ┌────────────────────────────────┐  │
│  │  Prefix Cache Lookup   ├─────────────►│ Re-use Cached KV Block Attention  │  │
│  └───────────┬────────────┘              └────────────────────────────────┘  │
│              │ Miss                                                          │
│              ▼                                                               │
│  ┌────────────────────────┐   Full Cache  ┌────────────────────────────────┐  │
│  │ Allocate Cache Block   ├─────────────►│ Evict Block (LRU / LFU Policy)    │  │
│  └────────────────────────┘              └────────────────────────────────┘  │
└────────────────────────────────────┬─────────────────────────────────────────┘
                                     │
                                     ▼
                       [ Optimized Context Window ]

**Core Subsystem Schemas**
from enum import Enum
from typing import Optional
from pydantic import BaseModel

class CachePolicy(str, Enum):
    LRU = "LRU"
    LFU = "LFU"

class ContextChunk(BaseModel):
    """Container for a chunk of text within a long document."""
    chunk_id: str
    content: str
    token_count: int
    start_token_idx: int
    end_token_idx: int
    parent_id: Optional[str] = None

class KVCacheBlock(BaseModel):
    """Simulated KV Cache memory block for a prompt prefix/chunk."""
    block_id: str
    chunk_id: str
    token_count: int
    last_accessed: float
    access_frequency: int = 1

class KVCacheStats(BaseModel):
    """Execution metrics for KV cache performance."""
    total_requests: int
    cache_hits: int
    cache_misses: int
    evictions: int
    active_blocks: int
    used_tokens: int
    hit_rate: float

### MISSION 22: AUTONOMOUS CODE EXECUTION SANDBOX & SECURITY POLICY ENGINE (`src/agent/code_sandbox.py`)

================================================================================
     MISSION 22: AUTONOMOUS CODE EXECUTION SANDBOX & SECURITY POLICY ENGINE
================================================================================

                         [ Agent Generated Code ]
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                             CodeSecurityAuditor                              │
│         (AST Static Tree Inspection & Dangerous Call Detection)              │
└───────────────────────────────────┬──────────────────────────────────────────┘
                                    │
             ┌──────────────────────┴──────────────────────┐
             │ Violations Found                            │ Clean Code
             ▼                                             ▼
┌──────────────────────────┐             ┌────────────────────────────────────┐
│ Security Violation Audit │             │        CodeExecutionSandbox        │
│   (Blocked Execution)    │             │  (Isolated Scope & Stdout Capture) │
└──────────────────────────┘             └─────────────────┬──────────────────┘
                                                           │
                                                           ▼
                                               [ Execution Result Output ]

**Core Architectural Components**
- `SecurityPolicy`: Defines dynamic security configurations, including forbidden imports (e.g., os, sys, subprocess), blocked functions (e.g., eval, exec, open), maximum output character limits, and execution timeouts.
- `CodeSecurityAuditor`: Statically inspects Python code using the Abstract Syntax Tree (ast) module without executing it, flagging unapproved imports or prohibited function calls.
- `CodeExecutionSandbox`: Safely executes pre-audited code within a restricted global/local scope, utilizing redirected `stdout` and `stderr` streams along with a structured `ExecutionResult` model.

### MISSION 23: MULTI-MODAL VISION & DOCUMENT PROCESSING AGENT (`src/agent/vision_document_agent.py`)

================================================================================
    MISSION 23: MULTI-MODAL VISION & DOCUMENT PROCESSING AGENT
================================================================================

                     [ Unstructured Visual Document / Image ]
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            DocumentVisualParser                              │
│       (Layout Segmentation, RoI BoundingBox Detection & OCR Grounding)       │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                             MultiModalVisionAgent                            │
│           (Visual Prompting + Layout Synthesis + Structured Schema)          │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │
                                       ▼
                        [ Structured Document Extraction ]
                         (JSON / Pydantic / VQA Answer)


**Core Subsystem Schemas**
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class ElementType(str, Enum):
    HEADER = "HEADER"
    PARAGRAPH = "PARAGRAPH"
    TABLE = "TABLE"
    IMAGE = "IMAGE"
    KEY_VALUE_PAIR = "KEY_VALUE_PAIR"

class BoundingBox(BaseModel):
    """Normalized coordinates [0.0, 1.0] for region of interest on document page."""
    x_min: float = Field(ge=0.0, le=1.0)
    y_min: float = Field(ge=0.0, le=1.0)
    x_max: float = Field(ge=0.0, le=1.0)
    y_max: float = Field(ge=0.0, le=1.0)

class DocumentLayoutElement(BaseModel):
    """A detected spatial element within a document page."""
    element_id: str
    element_type: ElementType
    bounding_box: BoundingBox
    raw_text: str
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)

class DocumentImage(BaseModel):
    """Metadata and raw payload wrapper for multi-modal document image inputs."""
    document_id: str
    width_px: int
    height_px: int
    image_bytes: Optional[bytes] = None
    page_number: int = 1

### MISSION 24: ENTERPRISE MULTI-TENANT LLM GATEWAY & RATE LIMITER (`src/core/llm_gateway.py`)

================================================================================
    MISSION 24: ENTERPRISE MULTI-TENANT LLM GATEWAY & RATE LIMITER
================================================================================

                         [ Inbound Multi-Tenant Request ]
                                        │
                                        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            EnterpriseLLMGateway                              │
│                (Tenant Identity & Token Auth Verification)                    │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                           TokenBucketRateLimiter                             │
│                  (RPM / TPM Sliding Bucket Rate Check)                       │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    │ (Quota OK)                          │ (Throttled / 429)
                    ▼                                     ▼
┌──────────────────────────────────────┐     ┌─────────────────────────┐
│       Provider Router & Fallback     │     │ RateLimitExceeded Exception│
│  (Primary Model ➔ Fallback Provider) │     └─────────────────────────┘
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│        Usage & Budget Metering       │
│    (Token Spend & Cost Tracking)     │
└──────────────────────────────────────┘

**Core Subsystem Schemas**
from pydantic import BaseModel, Field

class UsageQuota(BaseModel):
    """Defines usage limits for a specific tenant."""
    tenant_id: str
    max_rpm: int = Field(default=60, description="Requests Per Minute limit")
    max_tpm: int = Field(default=100_000, description="Tokens Per Minute limit")
    monthly_budget_usd: float = Field(default=100.0, description="Monthly USD spend cap")
    current_month_spend_usd: float = Field(default=0.0, description="Current accumulated spend")

class TenantContext(BaseModel):
    """Context holding tenant credentials and current usage state."""
    tenant_id: str
    api_key: str
    tier: str = Field(default="standard")
    quota: UsageQuota

### MISSION 25: REAL-TIME TELEMETRY, TRACING & OBSERVABILITY PIPELINE (`src/eval/telemetry_tracer.py`)

================================================================================
   MISSION 25: REAL-TIME TELEMETRY, TRACING & OBSERVABILITY PIPELINE
================================================================================

                     [ Agent / RAG Chain Execution ]
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                              ObservabilityTracer                             │
│       (Context Span Generator, Parent-Child Trace Hierarchy, Latency)        │
└───────────────────────────────────┬──────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            LLMTelemetryCollector                             │
│       (Token Consumption Counter, Cost Aggregator & Latency Percentiles)     │
└───────────────────────────────────┬──────────────────────────────────────────┘
                                    │
                                    ▼
                       [ Telemetry Summary & Tracing ]
                     (Trace Spans, Latency, Token Metrics)

### MISSION 26: PERSISTENT SEMANTIC MEMORY & HYBRID RETRIEVAL PIPELINE (`src/rag/persistent_memory.py`)

===================================================================================
        MISSION 26: PERSISTENT SEMANTIC MEMORY & HYBRID RETRIEVAL PIPELINE
===================================================================================
                      [ Query / Agent Context ]
                                 │
              ┌──────────────────┴──────────────────┐
              │                                     │
              ▼                                     ▼
┌───────────────────────────────────┐ ┌───────────────────────────────────┐
│        Dense Vector Search        │ │        Sparse BM25 Search         │
│   (Cosine Similarity Matching)    │ │   (TF-IDF / IDF Token Matching)   │
└─────────────────┬─────────────────┘ └─────────────────┬─────────────────┘
                  │                                     │
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        ReciprocalRankFusion (RRF)                       │
│    (Consolidated Reranking: RRF_Score = Sum(1 / (k + Rank_Model)))      │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      Dynamic Memory Pruner Engine                       │
│       (Timestamp Capacity Eviction & Context Window Optimization)       │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
                    [ Final Ranked Context Memory ]
                (Document Payloads, Relevance Scores & Metadata)

🧩 Core Architectural Components
1. MemoryDocument Model
    Role: Primary data wrapper representing an atomic unit of long-term memory.
    Fields: id (UUID/Hash), content (Raw Text Context), embedding (Dense Vector Float List), metadata (Dict KV Store), created_at (Datetime ISO Stamp).
2. SearchResult Schema
    Role: Unified output container encapsulating search hits, relevance scores, and rank orders.Fields: document (MemoryDocument instance), score (Cosine Sim / BM25 Score / Combined RRF Score), rank (Sequential 1-based Index).
3. PersistentMemoryEngine Core
    Dense Vector Search (_dense_search): Computes cosine similarity between incoming query vectors and stored embeddings.
    Sparse BM25 Search (_sparse_bm25_search): Computes term frequency-inverse document frequency keyword matching across stored document corpora.
    Reciprocal Rank Fusion (hybrid_search): Fuses multi-modal search ranks into a unified score via $\text{RRF Score}(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$.
    Dynamic Memory Pruning (prune_old_memories): Automatically evicts stale documents ordered by created_at timestamp when capacity limits (max_capacity) are breached.

===================================================================================
 MISSION 18 & 26: DUAL-TIER KNOWLEDGE & SEMANTIC RETRIEVAL PIPELINE
===================================================================================

                          [ Query / Context Payload ]
                                     │
                  ┌──────────────────┴──────────────────┐
                  │                                     │
                  ▼                                     ▼
┌───────────────────────────────────┐ ┌───────────────────────────────────┐
│  Persistent Memory Engine (# 26)  │ │      GraphRAG Engine (# 18)       │
│  ├─ Dense Vector Search (Cosine)  │ │  ├─ Entity / Relation Extraction  │
│  ├─ Sparse BM25 Search (Keywords) │ │  ├─ Property Graph Node Index     │
│  └─ RRF Hybrid Fusion             │ │  └─ Multi-Hop BFS Neighborhood    │
└─────────────────┬─────────────────┘ └─────────────────┬─────────────────┘
                  │                                     │
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      Context Synthesis & Reranker                       │
│    (Fuses Unstructured Semantic Chunks + Explicit Graph Fact Triples)   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
                     [ Consolidated Augmented Context ]

### MISSION 27: SELF-CORRECTION SANDBOX & CODE FEEDBACK LOOP (`src/sandbox/self_correction_engine.py`)

===================================================================================
 MISSION 27: SELF-CORRECTION SANDBOX & CODE FEEDBACK LOOP
===================================================================================

                        [ Generated Code Candidate ]
                                     │
                                     ▼
                      ┌─────────────────────────────┐
                      │ Code Execution Sandbox (#22)│
                      └──────────────┬──────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
              (Success: True)                  (Success: False)
                    │                                 │
                    ▼                                 ▼
         [ Return Execution Result ]      ┌───────────────────────┐
                                          │ Diagnostic Extractor  │
                                          │ (STDERR / Traceback)  │
                                          └───────────┬───────────┘
                                                      │
                                                      ▼
                                          ┌───────────────────────┐
                                          │ Feedback Generator    │
                                          │ & Reflection Prompt   │
                                          └───────────┬───────────┘
                                                      │
                                                      ▼
                                          ┌───────────────────────┐
                                          │ LLM Code Repairer     │
                                          │ (Attempt N / Max)     │
                                          └───────────┬───────────┘
                                                      │
                                                      └─► [ Loop to Sandbox (#22) ]

### MISSION 28: MULTI-TENANT DATA ISOLATION & SECURITY POLICY ENGINE (`src/core/tenant_security_engine.py`)

===================================================================================
 MISSION 28: MULTI-TENANT DATA ISOLATION & SECURITY POLICY ENGINE
===================================================================================

                    [ Inbound Request + SecurityContext ]
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    MultiTenantIsolationEngine Core                     │
│    (Tenant Registry, RBAC Policy Matcher & Session Validation)          │
└─────────────────────────────────────┬───────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
         (Access Validated)                    (Access Denied)
                    │                                   │
                    ▼                                   ▼
┌──────────────────────────────────────┐     ┌─────────────────────┐
│ Row-Level Security (RLS) Generator   │     │ Raise Permission    │
│ (Inject Tenant Metadata Filters)     │     │ Exception / Audit   │
└───────────────────┬──────────────────┘     └─────────────────────┘
                    │
                    ▼
       [ Isolated Vector & Graph RAG ]

===================================================================================
 MISSION 04/07: DUAL-PASS SECURITY GUARDRAILS PIPELINE
===================================================================================

                    [ Raw User Request / System Context ]
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       Guardrails Pass 1 (Input)                         │
│  ├─ Prompt Injection Detector & Jailbreak Classifier                    │
│  ├─ PII Masking (SSN, Emails, Tokens replaced with anonymized hashes)   │
│  └─ Toxicity & System Safety Threshold Validator                        │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
                   [ Executed Core Kernel / LLM Pipeline ]
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       Guardrails Pass 2 (Output)                        │
│  ├─ Generated Output Toxicity & Safety Verification                     │
│  ├─ PII Leakage Check & Secure Unmasking Mapping                        │
│  └─ Audit Logger (Structured Trace Logs for Compliance)                 │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
                       [ Verified Clean Output Response ]

### MISSION 29: DYNAMIC FINE-TUNING & ADAPTIVE LORA ADAPTER ROUTER (`src/core/lora_adapter_router.py`)

===================================================================================
 MISSION 29: DYNAMIC FINE-TUNING & ADAPTIVE LORA ADAPTER ROUTER
===================================================================================

                [ Classified Domain Intent & Tenant Context ]
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       LoRAAdapterRouter Core                            │
│  ├─ Tenant-Specific Domain Adapter Search                               │
│  ├─ Shared Enterprise Domain Adapter Fallback                           │
│  └─ Base Model Resolution (No Adapter)                                  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     Dynamic Weight Hot-Swapper                          │
│     (Swaps PEFT/LoRA matrices without reloading base model weights)      │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
                      [ Active Domain Model Runtime ]
             (Base LLM Backbone + Dynamically Injected LoRA Weights)

### MISSION 30: MULTI-MODAL RAG DOCUMENT PARSING & LAYOUT ANALYSIS ENGINE (`src/rag/multimodal_doc_parser.py`)

===================================================================================
 MISSION 30: MULTI-MODAL RAG DOCUMENT PARSING & LAYOUT ANALYSIS ENGINE
===================================================================================

                   [ Raw Unstructured PDF / Image Document Page ]
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           MultiModalDocParser Core                              │
│   (Spatial Bounding Box Resolution, Element Classification & Layout Analysis)   │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                             Parsed Document AST                                 │
│   ├─ Headers & Text Paragraphs (Direct Sparse/Dense Vector Embedding)          │
│   └─ Tables & Figures (Visual Embedding + Vision Agent Grounding #23)            │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │
                                         ▼
                 [ Structured Multimodal Document AST Payload ]
            (Ready for Dual-Tier Isolated Memory Retrieval #18 / #26)

### MISSION 31: KV-CACHE MULTI-MODAL VISUAL CONTEXT RETENTION ENGINE (`src/core/visual_kv_cache.py`)

===================================================================================
 MISSION 31: KV-CACHE MULTI-MODAL VISUAL CONTEXT RETENTION ENGINE
===================================================================================

                 [ Multi-Modal Document Page / Image Input ]
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       VisualKVCacheEngine Core                          │
│  ├─ Visual Prefix Hash Lookup (doc_id + page_number)                    │
│  ├─ Cache Hit  ➜ Fast-Path GPU KV-Tensor Reuse (Zero Re-encoding)        │
│  └─ Cache Miss ➜ ViT Encoding + LRU Eviction Capacity Budget Check      │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Active Visual Token Memory Pool                      │
│        (LRU Tracked Cache Entries with GPU Memory Buffer Pointers)      │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
                [ Direct LLM / Multi-Agent Multi-Turn Inference ]

1. Image Input ──► Mission 31 (Visual KV Cache): Heavy GPU Compute problem
                         └─► Instantly restores pre-encoded image patch tokens from GPU memory (bypasses ViT)
2. Text Input  ──► Mission 21 (Text KV Cache): Prevention of repetitive text computations
                         └─► Instantly restores previous conversation text tokens from KV Cache

===================================================================================
 MISSION 32: SELF-HEAVY AGENT CIRCUIT BREAKER & FALLBACK MESH
===================================================================================

       [ Autonomous Agent Execution Loop (# 20 / # 22 / # 27) ]
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    AgentCircuitBreaker Core                             │
│                                                                         │
│  State Machine Check:                                                   │
│    ├── 🟢 CLOSED    : Normal execution ──► Primary LLM/Tool Provider   │
│    ├── 🔴 OPEN      : Tripped ──────────► Bypasses Primary ──┐          │
│    └── 🟡 HALF-OPEN : Recovery Probe ──► Test Request Probe  │          │
└──────────────────────────────────┬────────────────────────┴─────────────┘
                                   │                        │
                       [ Primary Execution Fails /          │
                         Consecutive Failures >= 3 ]        │
                                   │                        │
                                   ▼                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          Fallback Mesh Router                           │
│  ├─ Redirects call to secondary provider (e.g., Local LLM / Backup API) │
│  ├─ Emits WARNING severity audit event to Telemetry Mesh (# 34)         │
│  └─ Returns safe degraded payload without crashing caller               │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
                                   ▼
                     [ Verified Execution Result ]

┌───────────────────────────────────────────────────────────┐
       │                                                           │
       ▼                                                           │
┌──────────────┐   Consecutive Failures >= Threshold   ┌──────────────┐
│  🟢 CLOSED   │ ────────────────────────────────────► │   🔴 OPEN    │
└──────────────┘                                       └──────────────┘
       ▲                                                       │
       │                                                       │
 Successful Probe                                  Timeout (10s) Elapsed
       │                                                       │
       │               ┌──────────────────┐                    │
       └───────────────│  🟡 HALF-OPEN    │ ◄──────────────────┘
                       └──────────────────┘
                         Probe Fails ──► Trips back to OPEN

State Machine: Manages operational state (CLOSED, OPEN, HALF_OPEN)(`CircuitState`).
Config Engine: Defines thresholds(failure_threshold=3, recovery_timeout_sec=10.0)(`CircuitBreakerConfig`).
Execution Wrapper: Intercepts agent tool/LLM calls and safely diverts to fallback_fn if primary fails or circuit is OPEN(`execute_with_fallback`).
Recovery Probe: Automatically switches OPEN → HALF_OPEN after the timeout to test if primary services have recovered(`check_state_transition`).

### MISSION 33: MULTI-AGENT CONSENSUS GRAPH & CONFLICT RESOLUTION ENGINE (`src/agent/consensus_graph.py`)

===================================================================================
 MISSION 33: MULTI-AGENT CONSENSUS GRAPH & CONFLICT RESOLUTION ENGINE
===================================================================================

                [ Divergent Multi-Agent Output Proposals (# 20) ]
                (Security Agent, Legal Agent, Code Reviewer, etc.)
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      ConsensusGraphEngine Core                          │
│  ├─ Domain Weight & Confidence Evaluation                               │
│  ├─ Weighted Score / Majority Vote / Highest Confidence Routing         │
│  └─ Conflict Arbitration & Proposal Convergence                         │
└──────────────────────────────────────┬──────────────────────────────────┘
                                       │
                                       ▼
                         [ ConsensusResult Payload ]
┌─────────────────────────────────────────────────────────────────────────┐
│                        ConsensusResult Payload                          │
│  ├─ winning_proposal_id & winning_content                               │
│  ├─ consensus_score (normalized agreement/confidence ratio)             │
│  └─ participating_agents tracking list                                  │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   ▼
            (Unified Verified Response ready for Guardrail Pass 2 # 4/7)
                                   ▼
            [ Cryptographic Audit Telemetry Mesh (# 34) ]

(`WEIGHTED_SCORE`(Default)) Critical domain tasks (e.g., Security/Legal) where expert agent votes carry more authority.$Score = \frac{Confidence \times Weight}{\sum Weight}$
(`MAJORITY_VOTE`) Fact-checking, multi-source RAG validation, or classification tasks.	Wins by highest accumulated agent weight for matching content.
(`HIGHEST_CONFIDENCE`) Fast-path single-agent winner selection without graph voting.$\max(Confidence\_Score)$ across all submitted proposals.

Input Payload: `agent_id`, `proposal_id`, `content`, `confidence_score` (0.0–1.0), and `agent_weight`(`AgentProposalStores`).
Engine Core: Evaluates divergent agent proposals and arbitrates conflicts using `resolve_consensus()`(`ConsensusGraphEngine`).
Strategy Enum: Configures arbitration policy (MAJORITY_VOTE, WEIGHTED_SCORE, HIGHEST_CONFIDENCE) (`ConsensusStrategy`).Output Payload: Outputs the winning proposal, final consensus score, and participating agent list(`ConsensusResult`).

### MISSION 34: ENTERPRISE AUDIT LOGGING, COMPLIANCE & TELEMETRY MESH (`src/eval/audit_telemetry_mesh.py`)

===================================================================================
 MISSION 34: ENTERPRISE AUDIT LOGGING, COMPLIANCE & TELEMETRY MESH
===================================================================================

       [ System Lifecycle Events: Security Check #28 / Guardrail Pass 2 #4/7 / Consensus #33 ]
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 AuditTelemetryMesh Core                                 │
│  ├─ Cryptographic SHA-256 Event Hashing & Chain Linking                                 │
│  ├─ Tenant-Isolated Audit Trail Partitioning                                            │
│  └─ Continuous Chain Tamper-Detection Verification Engine                               │
└────────────────────────────────────────┬────────────────────────────────────────────────┘
                                         │
                                         ▼
                     [ Tamper-Evident Immutable Audit Chain ]
             (Audit-Ready Payload for OpenTelemetry #25 & Benchmark #13)

### MISSION 35: REAL-TIME STREAM EVALUATOR & HALLUCINATION GUARD (`src/eval/stream_evaluator.py`)

===================================================================================
 MISSION 35: REAL-TIME STREAM EVALUATOR & HALLUCINATION GUARD
===================================================================================

                [ LLM Streaming Token Kernel Generator ]
                                   │
                                   ▼ (Raw Token Stream Generator)
┌─────────────────────────────────────────────────────────────────────────┐
│                   RealTimeStreamEvaluator Core                          │
│                                                                         │
│  Chunk-by-Chunk Evaluator & Interceptor:                               │
│    ├── Token Accumulator      : Appends chunks to running buffer       │
│    ├── Fast Grounding Matcher : Evaluates text against reference RAG   │
│    └── Hallucination Check    : Compares score against threshold       │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
                 ┌─────────────────┴─────────────────┐
                 │                                   │
   Score < Threshold (SAFE)            Score >= Threshold (BREACH)
                 │                                   │
                 ▼                                   ▼
┌─────────────────────────────────┐ ┌─────────────────────────────────┐
│      Safe Stream Forwarder      │ │    Early Termination Circuit    │
│  ├─ Emits SAFE chunk to client  │ │  ├─ Emits BLOCKED error chunk   │
│  └─ Continues stream generation │ │  └─ Immediately terminates loop │
└────────────────┬────────────────┘ └────────────────┬────────────────┘
                 │                                   │
                 └─────────────────┬─────────────────┘
                                   │
                                   ▼
          [ Cryptographic Audit Telemetry Mesh (# 34) Logging ]

Status Enum(`StreamSafetyStatus`): Operational status values (`SAFE`, `WARNING`, `HALLUCINATION_DETECTED`, `BLOCKED`).
Chunk Payload(`StreamChunkEvaluation`):	Contains chunk_index, text_chunk, accumulated_text, hallucination_score, and is_terminated.
Evaluator Engine(`RealTimeStreamEvaluator`):	Yields chunk evaluations in real-time and executes early-stopping via evaluate_stream().
Grounding Validator(_compute_chunk_hallucination_score()): Fast heuristic/embedding matcher checking ungrounded content against reference context.

### MISSION 36: AGENTIC SELF-HEALING CODE REFACTORING & AST VALIDATION SANDBOX (`src/agent/ast_refactor_sandbox.py`)

===================================================================================
 MISSION 36: AGENTIC SELF-HEALING CODE REFACTORING & AST VALIDATION SANDBOX
===================================================================================

                [ LLM / Agent Generated Code Snippet (# 20 / # 27) ]
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    ASTRefactorSandboxEngine Core                        │
│  ├─ AST Syntax Parse & Error Isolation (No execution risks)             │
│  ├─ AST Node Transformer (Auto-refactor bare except / flag eval)         │
│  └─ Source Unparse & ASTValidationResult Payload Generation             │
└────────────────────────────────────────┬────────────────────────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 │                                               │
           Syntax Valid                                    Syntax Invalid
                 │                                               │
                 ▼                                               ▼
┌─────────────────────────────────┐             ┌─────────────────────────────────┐
│   Safe Code Sandbox Execution   │             │   Self-Healing Agent Retry Loop │
│  (Docker / PyPy Sandbox # 22)   │             │   (Feeds error back to LLM # 27)│
└─────────────────────────────────┘             └─────────────────────────────────┘

### MISSION 37: MULTI-TENANT TOKEN RATE LIMITER, PRIORITY SCHEDULER & COST ALLOCATION MESH (`src/core/tenant_priority_scheduler.py`)

===================================================================================
 MISSION 37: MULTI-TENANT TOKEN RATE LIMITER & COST ALLOCATION MESH
===================================================================================

               [ Multi-Tenant API Request Ingress (# 28) ]
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   TenantPriorityScheduler Core                          │
│  ├─ Token Bucket SLA Check (Free: 5K, Pro: 25K, Enterprise: 100K TPM)   │
│  ├─ Priority Queue Routing (Enterprise: 100 > Pro: 50 > Free: 10)       │
│  └─ Micro-USD Token Cost Attribution & Billing Metrics                  │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
                 ┌─────────────────┴─────────────────┐
                 │                                   │
          Rate Limit OK                      Rate Limit Exceeded
                 │                                   │
                 ▼                                   ▼
┌─────────────────────────────────┐ ┌─────────────────────────────────┐
│ Execute LLM Pipeline & Record   │ │ 429 Too Many Requests Exception │
│ Cost Attribution Payload        │ │ (Logged to Audit Mesh # 34)     │
└─────────────────────────────────┘ └─────────────────────────────────┘
### MISSION 37: MULTI-TENANT TOKEN RATE LIMITER, PRIORITY SCHEDULER & COST ALLOCATION MESH (`src/core/tenant_priority_scheduler.py`)

===================================================================================
 MISSION 37: MULTI-TENANT TOKEN RATE LIMITER & COST ALLOCATION MESH
===================================================================================

               [ Multi-Tenant API Request Ingress (# 28) ]
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   TenantPriorityScheduler Core                          │
│  ├─ Token Bucket SLA Check (Free: 5K, Pro: 25K, Enterprise: 100K TPM)   │
│  ├─ Priority Queue Routing (Enterprise: 100 > Pro: 50 > Free: 10)       │
│  └─ Micro-USD Token Cost Attribution & Billing Metrics                  │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
                 ┌─────────────────┴─────────────────┐
                 │                                   │
          Rate Limit OK                      Rate Limit Exceeded
                 │                                   │
                 ▼                                   ▼
┌─────────────────────────────────┐ ┌─────────────────────────────────┐
│ Execute LLM Pipeline & Record   │ │ 429 Too Many Requests Exception │
│ Cost Attribution Payload        │ │ (Logged to Audit Mesh # 34)     │
└─────────────────────────────────┘ └─────────────────────────────────┘

### MISSION 38: AUTONOMOUS AGENTIC TOOL-USE REGISTRY & SCHEMA VALIDATOR (`src/agent/agent_tool_registry.py`)

===================================================================================
 MISSION 38: AUTONOMOUS AGENTIC TOOL-USE REGISTRY & SCHEMA VALIDATOR
===================================================================================

               [ Agent Function Call Intent Payload (# 20) ]
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    AgentToolRegistry Core                               │
│  ├─ Registry Lookup (Tool metadata & function lookup)                   │
│  ├─ JSON Parameter Schema & Type Safety Validation                      │
│  └─ Safe Dynamic Invocation & Error Encapsulation                       │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
                 ┌─────────────────┴─────────────────┐
                 │                                   │
          Schema Valid                        Schema Invalid
                 │                                   │
                 ▼                                   ▼
┌─────────────────────────────────┐ ┌─────────────────────────────────┐
│ Execute Tool & Return Result    │ │ Return Error Result to Agent    │
│ to Multi-Agent Orchestrator     │ │ Self-Healing Loop (# 27 / # 36) │
└─────────────────────────────────┘ └─────────────────────────────────┘