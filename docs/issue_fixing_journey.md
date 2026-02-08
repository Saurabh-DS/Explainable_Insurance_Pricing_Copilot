# Issue Fixing Journey: Insurance-Pricing-Copilot-RAG-MCP-AgenticAI

This document captures the technical challenges encountered during the development and optimization phase, and the systematic approach taken to resolve them.

---

## 1. Persistent "Emojis" in the UI
### Issue
Decorative elements (icons) remained in the UI despite code-level emoji removal logic.
### Root Cause
The icons were not actual Unicode emojis in the data, but **Streamlit's default framework avatars** (robot and user face icons) and success message icons (checkmarks).
### Resolution
1.  Modified `ui/streamlit_app.py` to set `avatar=None` in all `st.chat_message` calls.
2.  Set `icon=None` in all `st.success` calls.
3.  **Final Definitive Fix**: Injected custom CSS into the Streamlit app to force-hide `[data-testid="stChatMessageAvatarUser"]` and `[data-testid="stChatMessageAvatarAssistant"]` elements, ensuring a completely icon-free interface.

---

## 2. Environment Corruption & Stale State
### Issue
Changes to the code sometimes didn't appear in the running application, suggesting Docker cache or stale volume issues.
### Root Cause
Inconsistent cleanup between Docker runs led to orphaned containers and cached layers that didn't reflect the latest source.
### Resolution
1.  Created `clean_docker.ps1` (PowerShell) and `clean_docker.sh` (Bash).
2.  Scoped the scripts to remove **only project-specific** resources using `docker-compose down --rmi all --volumes --remove-orphans`.
3.  Ensured local project files (logs/reports) were preserved while the Docker internal state was surgically reset.

---

## 3. Cached Benchmarking Results
### Issue
Benchmarking results showed near-zero latency for repeated questions, making it impossible to measure actual "cold run" performance.
### Root Cause
The optimized pipeline's global semantic cache was returning immediate results for repeated queries during evaluation.
### Resolution
*   Implementation of a `bypass_cache` flag in the pipeline logic to ensure benchmarking always triggers a full execution cycle.

---

## 5. Accuracy Regression (Natural Language vs. Technical Names)
### Issue
Accuracy dropped from 100% to 33.3% as the LLM began using natural language ("high-risk postcode") instead of exact feature names ("postcode_risk").
### Root Cause
Increased explanation depth led the LLM to prioritize human-readable prose over the strict technical tags required by the evaluation script.
### Resolution
*   **Parentheses Fix**: Mandated that the LLM include the exact feature name in parentheses after natural language descriptions (e.g., "high risk (postcode_risk)"). This satisfied both human readability and technical verification metrics.

---

## 6. Latency Regression (Explanation Depth Overhead)
### Issue
The optimized pipeline's speed advantage over the baseline vanished (1.0x improvement) after implementing "Deep" explanations.
### Root Cause
The sheer volume of tokens generated for detailed reports took longer than the architectural optimizations saved.
### Resolution
1.  **True Parallelization**: Orchestrated RAG (Guideline Search) and Pricing to run concurrently, hiding ~0.5s of sequential wait.
2.  **Latency Dominance Optimization**: Implementing a high-density structured prompt and a strict `num_predict=250` token budget. 
3.  **Result**: Restored a 1.3x speedup while maintaining 77%+ concept coverage and 100% accuracy.
