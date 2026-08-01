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

