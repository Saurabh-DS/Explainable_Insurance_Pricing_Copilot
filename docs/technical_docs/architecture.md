# System Architecture

## Core Components

The application follows a **Microservices-in-a-Monolith** pattern, where logical services (Pricing, RAG, LLM) are decoupled via Python interfaces/APIs but deployed within a unified Docker network.

### 1. The LightGBM Pricing Engine (`pricing_model/`)
*   **Role**: The "Ground Truth" oracle.
*   **Model**: Gradient Boosted Regressor.
*   **Explainability**: Uses `shap.TreeExplainer` for exact feature attribution.
*   **Latency**: ~15ms for prediction, ~200ms for SHAP calculation (uncached).

### 2. The Vector Store (`rag/`)
*   **Role**: Knowledge Base for Unstructured Data.
*   **Technology**: `ChromaDB` (Persistent, Embedded).
*   **Embedding Model**: `all-MiniLM-L6-v2` (Default).
*   **Data**: Parsed `.txt` files from `data/guidelines`.

### 3. The Orchestrator (`pipelines/`)
*   **Baseline**: Uses `LangGraph` to construct a stateful graph where nodes are tools. Execution is determined by the LLM (ReAct).
*   **Optimized**: Uses `asyncio` to execute a high-concurrency **Wide Parallel Fork**.
    *   *Step 1*: Fork -> [Pricing + SHAP, **Hybrid Guideline Search (RAG)**, Similar Quotes].
    *   *Step 2*: Join -> synthesis_context.
    *   *Step 3*: **High-Density Synthesis** (Llama 3 with Token Budgeting).

### 4. The Interface Layer (`ui/`)
*   **Technology**: Streamlit.
*   **Role**: State management (`st.session_state`) stores the conversation history and configuration parameters. It polls the Backend Pipelines for responses.

## Data Flow Diagram

1.  **Ingestion**: `docker-compose up` triggers `init_db.py` -> Trains Model -> Indexes Guidelines -> Seeds SQL DB.
2.  **Request**: User submits data + query.
3.  **Processing**:
    *   **Vector Search**: Query -> Embedding -> ANN Search -> Guidelines.
    *   **SQL Search**: Profile -> SQL Query -> Similar Quotes.
    *   **Inference**: Profile -> Model -> Premium + SHAP.
4.  **Synthesis**: Data + Context -> LLM -> "Explanation".
5.  **Telemetry**: Timestamps -> MetricsCollector -> UI Dashboard.
