# 🏛️ System Architecture

This document describes the architectural design and flow of the `llm-engineering-lab` system.

---

## 1. Core Principles

1. **Schema-First Design:** All LLM outputs must be bound to Pydantic schemas to ensure deterministic, structured outputs.
2. **Environment Isolation:** Docker is used as the primary runtime to bypass local machine restrictions and ensure consistency across systems.
3. **Test-Driven Verification:** Every module must include unit tests with mocked API dependencies to enable zero-cost CI/CD validation.

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