# 04. Observability & Metrics: Measuring GenAI Performance

In production, "it works" isn't enough. We need to know *how well* it works. This project implements a comprehensive custom telemetry stack to monitor every millisecond.

## Key Metrics Explained

The dashboard displays these real-time metrics for every run:

### 1. Total Latency
*   **Definition**: The wall-clock time from the user clicking "Run" to receiving the full answer.
*   **Benchmark**: Target is < 2.0s for a smooth UX.

### 2. Time to First Token (TTFT)
*   **Definition**: How long the user looks at a blank screen before the text starts appearing.
*   **Significance**: This is heavily influenced by the **Prompt Size** (Prompt Prefill Time). Our "Prompt Compression" optimization directly targets this.

### 3. Tokens Per Second (TPS)
*   **Definition**: The speed of text generation.
*   **Significance**: A measure of the LLM's raw throughput. It helps distinguish between "System Slowness" (Pipeline issues) and "Model Slowness" (GPU/Ollama issues).

### 4. Semantic Cache Latency
*   **Definition**: The time taken to generate a query embedding and search the cache.
*   **Insight**: Typically < 0.05s. This metric proves that the "Cache Check" overhead is negligible compared to the massive gain of a Cache Hit.

## Implementation Details

### The `MetricsCollector` Class (`observability/metrics.py`)
We built a custom singleton wrapper that travels through the pipeline:
1.  **Timer Context Manager**: A python context manager (`with measure_time('component'):`) automatically captures duration.
2.  **Metadata Extraction**: We extract raw nanosecond timestamps directly from Ollama's API response (`response_metadata`) to get accurate model-internal timings, bypassing network jitter.

### Side-by-Side Comparison UI
The Streamlit interface acts as an **A/B Testing Platform**:
*   **Left Column**: Baseline (Control Group).
*   **Right Column**: Optimized (Test Group).
*   **Bottom Table**: granular diff of every metric.

This allows immediate visual confirmation of performance engineering efforts (e.g., seeing the "Prompt Tokens" drop from 500 to 150).
