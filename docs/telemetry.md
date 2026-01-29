# Production Telemetry & Monitoring

In a production system, you need to know **how long** things take and **where** they fail. This project now includes a built-in monitoring layer.

## 📊 Captured Metrics

1.  **Total Latency**: The time from user click to explanation display.
2.  **Node Latency**:
    -   `pricing_latency_ms`: Time to run LightGBM and SHAP.
    -   `guidelines_latency_ms`: Time to search ChromaDB for underwriting rules.
    -   `similarity_latency_ms`: Time to find similar historical quotes in SQLite.
    -   `llm_latency_ms`: Time taken by Ollama to generate the final explanation.

## 🛠️ How it's implemented

### 1. Database Layer (`database/quotes.db`)
A new table `telemetry` stores every request with its timestamp, input data, status, and precise latency measurements.

### 2. Instrumentation (`agent/graph.py`)
Each node in the LangGraph agent is wrapped with timing logic:
```python
start_time = time.time()
# ... logic ...
latency = (time.time() - start_time) * 1000
```

### 3. API Layer (`api/main.py`)
FastAPI captures the end-to-end request time and writes a row to the database after every successful or failed analysis.

### 4. Monitoring UI (`ui/app.py`)
A dedicated **Monitoring Dashboard** tab in Streamlit calls the `/telemetry` endpoint to show:
-   Average Latency (ms)
-   Total Request Count
-   Error Rates
-   Detailed Request Logs

## 🚀 Why this is "Production Grade"
- **Observability**: You can identify if the LLM is slowing down or if the database is lagging.
- **Auditability**: Every analysis is saved, allowing you to debug why certain inputs resulted in specific explanations.
- **Scalability**: The telemetry schema is ready to be exported to tools like Prometheus or ELK stack.
