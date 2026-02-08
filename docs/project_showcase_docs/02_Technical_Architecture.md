# 02. Technical Architecture & System Design

## High-Level Stack
This project is built as a modular, containerized application using industry-standard tools for Machine Learning and GenAI.

*   **Frontend**: `Streamlit` (Python) - Interactive Chat UI, Metrics Dashboard, and parameter controls.
*   **Backend API**: `FastAPI` (Python) - Serves the pricing model and orchestration logic.
*   **LLM Serving**: `Ollama` (Local Inference) - Running **Llama 3 (8B)** locally for data privacy and zero cost.
*   **Orchestration**: `LangChain` / `LangGraph` - Managing the agentic state, tools, and conversation flow.
*   **Vector Database**: `ChromaDB` - Storing embeddings of Underwriting Guidelines for RAG.
*   **ML Model**: `LightGBM` (Gradient Boosting) - The core pricing model being explained.
*   **Explainability**: `SHAP` (SHapley Additive exPlanations) - Model-agnostic feature importance.

## System Architecture Diagram
```mermaid
graph TD
    User[User (Analyst/Underwriter)] -->|Query| UI[Streamlit UI]
    UI -->|Request| Pipeline{Optimization Check}
    
    subgraph "Baseline Agent"
        Pipeline -->|Route: Baseline| Agent[LangGraph Agent]
        Agent -->|Serial Call| Tool1[Pricing Model + SHAP]
        Agent -->|Serial Call| Tool2[ChromaDB (Guideline RAG)]
        Agent -->|Serial Call| Tool3[SQLite (Similar Quotes)]
        Tool3 --> LLM1[Llama 3 via Ollama]
    end
    
    subgraph "Optimized Pipeline (Async Parallel)"
        Pipeline -->|Route: Optimized| CacheCheck{Semantic Cache?}
        CacheCheck -->|Hit| Instant[Instant Response]
        CacheCheck -->|Miss| AsyncMgr[Asyncio Orchestrator]
        
        subgraph "Parallel Execution Tier"
            AsyncMgr -->|Concurrent| T1[Pricing + SHAP]
            AsyncMgr -->|Concurrent| T2[Embedding Calc]
            AsyncMgr -->|Concurrent| T3[Similar Quotes]
        end
        
        T1 & T2 & T3 --> PromptEng[High-Fidelity Prompt]
        PromptEng -->|Global Client| RAG[Vector Search (Top-2)]
        
        RAG -->|Regex Parse| LLM2[Llama 3 (Unconstrained)]
    end
    
    LLM1 & LLM2 & Instant --> UI
```

## Core Components

### 1. The Pricing Engine (`pricing_model/`)
*   **Model**: A LightGBM Regressor trained on 15,000 synthetic insurance policies.
*   **SHAP**: A `TreeExplainer` is used to calculate exact SHAP values. This quantification is the "ground truth" for the explanation.

### 2. The Retrieval System (RAG) (`rag/`)
*   **Ingestion**: Parses raw text/PDF guidelines (e.g., "Young Driver Policy 2024").
*   **Embedding**: Uses `ChromaDB`'s default embedding model (all-MiniLM-L6-v2) to convert text to vectors.
*   **Retrieval**: Given a query (or a Top Feature like "Age"), it finds the most relevant policy chunks.

### 3. The Agent / Pipeline (`pipelines/`)
*   **Baseline**: A standard ReAct (Reason + Act) agent that "thinks" about which tool to use next. It is flexible but slow due to serial execution and verbose "thought" tokens.
*   **Optimized**: A hard-coded, parallelized DAG (Directed Acyclic Graph) that knows *exactly* what steps to take (Price -> Guidelines -> Explanation), bypassing the overhead of agentic reasoning for this specific task.

## Data Flow
1.  **User Input**: "Why is the premium £1200?"
2.  **Telemetry**: Request is time-stamped; Latency tracking starts.
3.  **Preprocessing**: Input profile (Age: 20, postcode: High Risk) is converted to model features.
4.  **Inference**: 
    *   Model predicts £1200.
    *   SHAP reveals "Age" added +£400.
5.  **Contextualiataion**:
    *   RAG searches for "Age < 25" in guidelines. Found: "Load 20% for under 21s".
    *   DB searches similar quotes. Found: "Average for Age 20 is £1150".
6.  **Synthesis**: LLM combines these 3 facts into a narrative.
7.  **Output**: Response streamed to UI + Metrics (Token count, Latency) logged.
