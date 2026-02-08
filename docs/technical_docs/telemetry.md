# Telemetry & Observability

This project implements a full-stack observability layer designed to treat Generative AI output as a measurable engineering problem.

## The Metrics Collector

Located in `observability/metrics.py`, the `MetricsCollector` class provides a unified interface for tracking the lifespan of a user request.

### Key Performance Indicators (KPIs)

#### 1. End-to-End Latency
The single most important metric for User Experience (UX). It captures time from "Button Click" to "Response Complete".
*   **Target**: < 11.0 seconds for Deep Analyst Reports.

#### 2. Semantic Cache Check Duration
*   **New Metric**: Measures the time taken to:
    1.  Vectorize the incoming query.
    2.  Perform a vector similarity search against the cache.
*   **Insight**: This typically takes **10-40ms**. Tracking this proves that the "cost" of checking the cache is negligible compared to the "saving" of a cache hit (avoiding a 10s generation).

#### 3. Time-to-First-Token (TTFT)
Derived from Ollama's `prompt_eval_duration`. This measures how responsive the system *feels*. High TTFT usually indicates an overly large Prompt Context logic (Retrieval of too many documents).

#### 4. Tokens Per Second (TPS)
Derived from `eval_duration` / `eval_count`. This monitors the raw inference capacity of the local hardware.
*   **Optimization**: If TPS drops, it suggests resource contention (CPU/RAM exhaustion) rather than code inefficiency.

## Dashboard Visualization

The Streamlit UI consumes these metrics to render the **System Telemetry** table.

### Comparative Telemetry
In "Comparison Mode", metrics are displayed side-by-side:

| Metric | Baseline | Optimized | Delta |
| :--- | :--- | :--- | :--- |
| **Total Latency** | ~13.4s | **~10.4s** | **-22%** |
| **Concept Coverage** | 58.3% | **77.8%** | **+20% Richer** |
| **Driver Accuracy** | 100% | **100%** | **-** |

This granular visibility allows developers to pinpoint exactly *where* the optimization gains are coming from (e.g., "We saved 0.5s by parallelizing tools" vs "We saved 3.0s by distilling the prompt").
