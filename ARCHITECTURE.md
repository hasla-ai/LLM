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

                    