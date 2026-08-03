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
                                                            ▼
                                    ┌───────────────────────────────────────────────┐
                                    │ Enterprise Multi-Tenant Gateway & Rate Limiter│ (# 24)
                                    │  -> Token Bucket Rate Limiter                 │
                                    └───────────────────────┬───────────────────────┘
                                                            │
                 ┌──────────────────────────────────────────┴────┐
                 │                                               │
                 ▼ (Visual / Image / Doc)                        ▼ (Text / Prompt Query)
┌─────────────────────────────────┐             ┌─────────────────────────────────┐
│ Multi-Modal Vision              │ (# 23)      │ Adaptive RAG Router             │ (# 12)
│ & Document Agent                │             └────────────────┬────────────────┘
└────────────────┬────────────────┘                              │
                 │              ┌────────────────────────────────┼────────────────────────────────┐
                 │              │ (SIMPLE)                       │ (CODE_EXECUTION)               │ (COMPLEX)
                 │              ▼                                ▼                                ▼
                 │  ┌───────────────────────┐        ┌───────────────────────┐        ┌───────────────────────┐
                 │  │ Direct LLM Inference  │        │ Code Execution        │ (# 22) │ Multi-Agent Debate    │ (# 20)
                 │  │                       │        │ Sandbox Engine        │        │ Engine                │
                 │  └───────────┬───────────┘        └───────────┬───────────┘        └───────────┬───────────┘
                 │              │                                │                                │
                 │              └────────────────────────────────┼────────────────────────────────┘
                 │                                               │
                 │                                               ▼
                 │                               ┌───────────────────────────────┐
                 │                               │ Hierarchical Chunker          │ (# 21)
                 │                               │ & KV Cache                    │
                 │                               └───────────────┬───────────────┘
                 │                                               │
                 │                                               ▼
                 │                               ┌───────────────────────────────┐
                 │                               │ GraphRAG Engine               │ (# 18)
                 │                               │ (Multi-Hop Graph)             │
                 │                               └───────────────┬───────────────┘
                 │                                               │
                 └───────────────────────────────────────────┬───┘
                                                             │
                                                             ▼
                                     ┌───────────────────────────────────────────────┐
                                     │ Model Distillation Engine                     │ (# 17)
                                     │ (Synthetic LoRA Trainer)                      │
                                     └───────────────────────┬───────────────────────┘
                                                             │
                                                             ▼
                                     ┌───────────────────────────────────────────────┐
                                     │ LLM Security Guardrails                       │ (# 4/7)
                                     │ (PII Sanitizer & Audit)                       │
                                     └───────────────────────┬───────────────────────┘
                                                             │
                                                             ▼
                                     ┌───────────────────────────────────────────────┐
                                     │ 🧠 Persistent Memory RAG                      │ (# 26)
                                     │  ├─ Dense Vector Engine (Cosine Sim)          │
                                     │  ├─ Sparse BM25 Engine (TF-IDF/IDF)           │
                                     │  └─ Reciprocal Rank Fusion (RRF)              │
                                     └───────────────────────┬───────────────────────┘
                                                             │
                                                             ▼
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

### MISSION 27: GRAPHRAG & KNOWLEDGE GRAPH MEMORY ENGINE (`src/rag/graph_memory.py`)

===================================================================================
 MISSION 27: GRAPHRAG & KNOWLEDGE GRAPH MEMORY ENGINE
===================================================================================

                    [ Context Fact / Query Input ]
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     Entity & Relation Extractor                         │
│       (Source Entity) ─────[ Relation Type ]─────> (Target Entity)      │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    KnowledgeGraphMemoryEngine Core                      │
│   (Entity Indexing, Relation Weights & Case-Insensitive Deduplication)  │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Multi-Hop BFS Subgraph Traverser                     │
│         (Max-Hops Traversal, Fact Triples & Subgraph Extraction)         │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
                     [ Extracted Graph Context ]
             (Entity Nodes, Relation Edges & Fact Triples)

             