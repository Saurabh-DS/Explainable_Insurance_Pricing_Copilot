# 05. Codebase Walkthrough

A guide to the project structure to help navigate the key logic.

## Directory Structure

```text
Explainable_Insurance_Pricing_Copilot/
├── ui/                     # Frontend
│   └── streamlit_app.py    # The Main Dashboard logic. Handles Chat, State, and Comparisons.
├── pipelines/              # Orchestration Logic
│   ├── baseline_pipeline.py  # Wraps the LangGraph Agent (Slow, Legacy).
│   └── optimized_pipeline.py # The Star of the Show. Parallel, Cached, Hardened Pipeline.
├── agent/                  # Legacy Agent
│   └── graph.py            # LangGraph definition (Nodes, Edges, State).
├── pricing_model/          # ML Core
│   ├── train_model.py      # Trains LightGBM on synthetic data.
│   └── predict.py          # Inference + SHAP Explainability logic.
├── rag/                    # Retrieval Augmented Generation
│   └── build_vector_store.py # Ingests PDF/Text guidelines into ChromaDB.
├── mcp_server/             # "Tools" Layer
│   └── server.py           # Exposes Guidelines Search & Similar Quotes to the Agent.
├── observability/          # Telemetry
│   ├── metrics.py          # Data classes for collecting latency/tokens.
│   └── timer.py            # Utility for timing code blocks.
├── data/                   # Input Data
│   └── guidelines/         # Raw text files (policies).
├── docker-compose.yml      # Container orchestration
└── Dockerfile              # Container definition
```

## Key Files to Show in Interview

### 1. `pipelines/optimized_pipeline.py`
**Why:** This contains all the engineering magic.
*   **Parallel Orchestration**: Show `run_optimized_pipeline_async` using `asyncio.gather` to hide embedding latency.
*   **Global State**: Show `get_underwriting_collection` pattern to eliminate DB init overhead.
*   **High-Speed Decoding**: Show `extract_json` (Regex) which replaces slow constrained decoding.
*   **Prompt Hardening**: Show the "High Fidelity" system prompt that guarantees 100% accuracy.

### 2. `ui/streamlit_app.py`
**Why:** It shows how you present data to stakeholders.
*   Show how `base_res` and `opt_res` are run side-by-side.
*   Show the metric calculation logic (TPS/TTFT).

### 3. `observability/metrics.py`
**Why:** It shows you care about production standards.
*   Show the `PipelineMetrics` dataclass—structured logging, not just print statements.

### 4. `Dockerfile`
**Why:** It shows DevOps awareness.
*   Multi-stage build (or at least clean structure).
*   Pre-baking models (`python train_model.py` in build step) so runtime is fast.
