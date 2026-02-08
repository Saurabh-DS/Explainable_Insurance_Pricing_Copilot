# Comprehensive Interview Q&A: Insurance-Pricing-Copilot-RAG-MCP-AgenticAI

This document prepares you for deep-dive technical and product interviews. It covers the "Whys", the "What Ifs", and the "Alternatives".

---

## Architecture & System Design

### Q: Why did you choose a "Modular Monolith" over Microservices?
**A:**
*   **Simplicity**: For a team of 1-3 developers, managing 5 separate repo deployments (UI, API, VectorDB, Model, LLM) creates massive "DevOps Tax".
*   **Latency**: Internal function calls in Python are nanoseconds. HTTP calls between microservices are milliseconds. For a latency-critical "Copilot", keeping the RAG and Pricing logic in-process (or same network) minimizes overhead.
*   **Evolution**: It is easier to split a clean monolith into microservices later than to merge distributed spaghetti back together. The code is modular (`pipelines/`, `pricing_model/`), so splitting `pricing_model` into its own container later would be trivial.

### Q: Why Streamlit? Isn't it just for prototypes?
**A:**
*   **Velocity**: React/Next.js would require 2 weeks of boilerplate. Streamlit took 2 days.
*   **Audience**: The users are internal Analysts. They value *functionality* and *data density* over consumer-grade animations.
*   **Native Data Support**: Streamlit handles Pandas interaction and charting out-of-the-box, which is 90% of what this tool does.

### Q: Why did you build the "Optimized Pipeline" using raw Asyncio instead of just tweaking the Agent?
**A:**
*   **Determinism**: Agents are non-deterministic loopers. In Pricing, we have a fixed workflow: `Predict -> Search -> Explain`. We don't need the Agent to "decide" to check the price; we *always* want it to checks the price.
*   **Overhead**: A standard ReAct Agent generates ~50-100 tokens of "thought" per step (*"I need to check the price..."*). This adds latency and cost. A hardcoded Asyncio DAG has zero reasoning overhead.

---

## GenAI & LLM Decisions

### Q: Why RAG (Retrieval Augmented Generation) instead of Fine-Tuning Llama 3?
**A:**
*   **Knowledge Updates**: Insurance guidelines change monthly. Fine-tuning a model every month is expensive and slow. Updating a Vector Database is instant (cron job).
*   **Citation/Trust**: RAG allows us to show *exactly* which document chunk was used. Fine-tuning hides the source in the model's weights ("Hallucination risk").
*   **Privacy**: We are not baking proprietary pricing rules into the model weights, making it safer to swap models later.

### Q: Why Llama 3 (8B) locally? Why not GPT-4?
**A:**
*   **Data Privacy**: Insurance pricing data is highly sensitive. Sending customer profiles to OpenAI APIs might violate GDPR/Compliance. Local execution guarantees data never leaves the VPC.
*   **Unmetered Cost**: internal tools have high usage. Paying per-token to OpenAI adds up. Running on fixed hardware (GPU) is a predictable Flat Cost.
*   **Latency Stability**: Public APIs have jitter. Local inference is consistent.

### Q: How do you handle "Hallucinations" where the AI invents a discount?
**A:**
1.  **Grounding**: The System Prompt explicitly says: *"Answer ONLY using the provided Context. If you don't know, say you don't know."*
2.  **SHAP Anchor**: The AI is forced to explain the *mathematical* SHAP values provided. It cannot invent numbers because the numbers are inputs, not generations.
3.  **Low Temperature**: We run at `Temperature=0` for maximum determinism.

---

## Performance & Optimization

### Q: You mentioned "Semantic Caching". What happens if the cache gets too big?
**A:**
*   **TTL (Time To Live)**: We would implement an expiry policy (e.g., 24 hours) because pricing rules change.
*   **LRU (Least Recently Used)**: Currently, we use a simple dictionary, but in production, we would use Redis with an implementation that evicts the oldest unused queries when memory fills up.
*   **Vector Index**: Enhancing the cache lookup with a FAISS index instead of a linear scan would maintain speed even with millions of cached queries.

### Q: Asyncio `gather` is good, but what if the Pricing Model crashes? Does the whole request fail?
**A:**
*   **Current State**: Yes, `asyncio.gather` effectively waits fo all.
*   **Improvement**: We could use `return_exceptions=True` to allow the "Similar Quotes" and "RAG" parts to succeed even if "Pricing" fails, allowing the UI to show a partial response ("I found guidelines, but the pricing engine is down...").

---

## Alternatives & Trade-offs ("What if not this?")

### Q: Alternative to ChromaDB?
*   **PGVector (PostgreSQL)**: If we already had a Postgres DB for the app, adding the vector extension would reduce infrastructure complexity (one less DB to manage).
*   **Pinecone/Weaviate**: Managed services. Good for scaling to billions of vectors, but overkill for internal enterprise docs (usually < 100k chunks) and breaks the "Local/Air-gapped" requirement.

### Q: Alternative to SHAP?
*   **LIME**: Faster but less theoretically sound (local linear approximation vs game theory).
*   **Integrated Gradients**: Better for Neural Networks, but we are using Tree-based models (LightGBM), where SHAP is the gold standard.

### Q: Alternative to LangChain?
*   **LlamaIndex**: Excellent for the RAG part (maybe even better), but LangChain/LangGraph offers more control over the "Agentic" state machine for the Baseline comparison.
*   **DSPy**: Emerging framework for "programming" prompts. Very promising for optimizing the prompt automatically rather than manual engineering.

---

## Business & ROI Questions

### Q: How do you measure the ROI of this system?
**A:**
1.  **Time Savings**: Average investigation time drops from 4 hours -> 5 minutes.
2.  **Compliance Risk**: Consistency in explanations reduces the risk of FCA fines for "unfair pricing".
3.  **Conversion**: Better explanations to brokers lead to higher sales conversion.

### Q: What is the maintenance cost?
**A:**
*   **Model Drift**: We need to re-run SHAP baselines if the underlying LightGBM model is retrained.
*   **Document Ingestion**: We need a pipeline (CI/CD) to ingest new PDF guidelines automatically when the Underwriting team uploads them.

---

## Scalability & Limits

### Q: This runs on one machine. How would you scale it to 10,000 concurrent users?
**A:**
1.  **Decouple Inference**: Move the `ollama-backend` to a dedicated GPU cluster (e.g., Kubernetes + Ray Serve or vLLM).
2.  **Load Balancing**: Run multiple instances of the `insurance-api` (FastAPI) behind an Nginx load balancer.
3.  **Vector DB Scaling**: Migrate from local ChromaDB to a managed Qdrant or Pinecone cluster for distributed indexing.
4.  **Async Queue**: Introduce a message queue (RabbitMQ/Kafka) between the API and the LLM workers so requests don't time out during spikes.

### Q: What is the bottleneck? CPU, GPU, or IO?
**A:**
*   **Primary Bottleneck**: **GPU Compute** (LLM Token Generation). This is the slowest part.
*   **Secondary**: **Embedding Generation** for RAG (CPU/GPU).
*   **Least Concern**: The Python code/FastAPI overhead is negligible.

---

## Testing & Quality Assurance

### Q: How do you test a GenAI application?
**A:**
*   **Deterministic Tests**: Unit tests for the Pricing Model and Math helper functions.
*   **Evals (LLM-as-a-Judge)**: We run a "Golden Dataset" of questions. We use a stronger model (e.g., GPT-4) to grade our Llama 3 responses on "Faithfulness" (did it make things up?) and "Coherence".
*   **Regression Testing**: We track the "Answer Vector Similarity" over time. If code changes cause the answer embedding to drift significantly for the same input, we flag it.

---

## Security & Compliance (Restored)

### Q: Is this GDPR compliant?
**A:**
*   **Local Execution**: Yes. No data leaves the VPC.
*   **Right to Forgotten**: We can delete a user's pricing profile from SQLite easily. Vector stores can be re-indexed without that user's specific context if necessary.
*   **Explanation**: The core feature of this tool *is* the GDPR "Right to Explanation".

### Q: How do you validate that the explanation is mathematically correct?
**A:**
*   **SHAP Fidelity**: We do not let the LLM guess the feature importance. We calculate it using `shap.TreeExplainer` (exact method). The LLM is only allowed to *narrate* these pre-calculated numbers.
*   **Guardrails**: We can implement a post-processing step that regex-matches the numbers in the text against the actual inputs. If they don't match, we block the response.

---

## Future Roadmap

### Q: What would you build next?
**A:**
1.  **Feedback Loop**: Add Thumbs Up/Down buttons in the UI to collect RLHF (Reinforcement Learning from Human Feedback) data.
2.  **Multi-Modal RAG**: Allow the model to "see" charts (images) in the guidelines, not just text.
3.  **Active Learning**: If the confidence score is low, automatically route the query to a senior human underwriter.

