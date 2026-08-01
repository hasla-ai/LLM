## 🏗️ `ARCHITECTURE.md`

Save this file at the root of your project: **`ARCHITECTURE.md`**

```markdown
# 🏛️ System Architecture

This document describes the architectural design and flow of the `llm-engineering-lab` system.

---

## 1. Core Principles

1. **Schema-First Design:** All LLM outputs must be bound to Pydantic schemas to ensure deterministic, structured outputs.
2. **Environment Isolation:** Docker is used as the primary runtime to bypass local machine restrictions and ensure consistency across systems.
3. **Test-Driven Verification:** Every module must include unit tests with mocked API dependencies to enable zero-cost CI/CD validation.

---

## 2. Mission 1: Structured LLM Client Flow
+------------------+         +--------------------------+         +----------------------+
|                  |         |                          |         |                      |
|  User Request /  | ------> |   StructuredLLMClient    | ------> |    OpenAI API /      |
|  Prompt Input    |         |  (Pydantic Schema Guard) |         |  Structured Parse    |
|                  |         |                          |         |                      |
+------------------+         +--------------------------+         +----------------------+
|                                  |
| Validate Output                  | Raw Response
v                                  v
+--------------------------+         +----------------------+
|   Validated Pydantic     | <------ |  Structured JSON     |
|   Python Object (T)      |         |  Object              |
+--------------------------+         +----------------------+

### Data Flow Specification
1. The user defines a target response schema extending `pydantic.BaseModel`.
2. `StructuredLLMClient.generate_structured()` wraps OpenAI's `chat.completions.parse` endpoint.
3. The response is validated against the schema. If validation passes, a strongly-typed Python object is returned.

---

## 3. Testing Strategy (Mocking Pipeline)
+-------------------------+
|  Pytest Execution       |
+-------------------------+
|
v
+-------------------------+       Mocked Output       +--------------------------+
|  test_llm_client.py     | ------------------------> |   StructuredLLMClient    |
+-------------------------+                           +--------------------------+
|                                                      |
| Asserts Type & Constraints                            | Intercepts Call
v                                                      v
+-------------------------+                           +--------------------------+
|  PASSED Assertion       | <------------------------ |   MagicMock Return       |
+-------------------------+                           +--------------------------+
* **No Network Side-Effects:** Tests mock network interactions with `unittest.mock.MagicMock`.
* **Zero API Costs:** Mocked testing ensures suite execution takes < 1 second with 0 API consumption.
