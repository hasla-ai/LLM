# 🚀 LLM Engineering Lab (`llm-engineering-lab`)

A hands-on, test-driven repository for building production-grade LLM applications, RAG pipelines, and Autonomous Agent systems.

Every module in this repository is built with **strict type validation**, **Docker containerization**, and **automated Pytest suites**.

---

## 📂 Project Structure

```text
llm-engineering-lab/
├── Dockerfile                  # Containerized environment for isolated execution
├── pyproject.toml              # Dependencies & Pytest configuration
├── requirements.txt            # Python package dependencies
├── ARCHITECTURE.md             # High-level architecture documentation
├── src/
│   ├── core/                   # LLM inference & schema validation engines
│   │   ├── __init__.py
│   │   └── llm_client.py       # Structured LLM Client (Pydantic + OpenAI)
│   └── rag/                    # Retrieval-Augmented Generation pipeline
│       ├── __init__.py
│       ├── vector_store.py     # Vector Store & Cosine Similarity search
│       └── rag_pipeline.py     # RAG Orchestrator
└── tests/                      # Automated Pytest suite
    ├── __init__.py
    ├── test_llm_client.py
    └── test_rag.py
```
🛠️ Mission Progress
[x] Mission 1: Project Setup & Structured Inference Engine

Docker containerization for zero-dependency execution.

Type-safe LLM client using Pydantic schema enforcing (StructuredLLMClient).

Unit tests with unittest.mock for fast, cost-free CI/CD verification.

[ ] Mission 2: In-Memory Vector Store & RAG Pipeline

Cosine similarity search & vector indexing.

Context synthesis with source attribution.

[ ] Mission 3: Agentic Workflows & Tool Calling (Upcoming)

🚀 Quick Start (Docker)
1. Set Environment Variables
Copy .env.example to .env and add your OpenAI API Key:

``` bash
cp .env.example .env
```

2. Run Test Suite via Docker
Run unit tests inside the isolated Docker container:

```bash
# Build the Docker image
docker build -t llm-lab .

# Run tests with volume mounting
docker run --rm --env-file .env -v $(pwd):/app llm-lab
```

feat: initial project setup and structured LLM client with unit tests
('initial_project_setup.txt')
