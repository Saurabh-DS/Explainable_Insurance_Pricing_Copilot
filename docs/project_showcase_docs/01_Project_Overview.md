# 01. Project Overview: Explainable AI (XAI) Insurance Pricing Copilot

## The "Why" - Problem Statement
In the modern insurance industry, pricing models (like Gradient Boosted Trees, Neural Networks) are becoming increasingly complex. While they are accurate, they are **"Black Boxes"**. 

This creates three critical problems:
1.  **Regulatory Compliance**: Regulators (like the FCA, GDPR) demand "Right to Explanation". You cannot quote a high premium without being able to explain *why* to the customer.
2.  **Internal Trust**: Pricing Analysts and Underwriters often distrust model outputs if they defy intuition (e.g., "Why did the price jump 20% for this safe driver?").
3.  **Operational Inefficiency**: Investigating a single pricing anomaly currently takes an analyst hours of manual SQL queries, Excel crunching, and digging through PDF guidelines.

## The Solution - Agentic GenAI Copilot
This project is an **"Internal AI Copilot"** designed specifically for Pricing Analysts, Underwriters, and Audit teams. 

It is NOT just a chatbot. It is a **Compound AI System** that orchestrates multiple tools to provide a **Holistic Explanation**:
1.  **Quantitative Reasoning**: It interprets the "Black Box" model using **SHAP (SHapley Additive exPlanations)** values to mathematically quantify which features (Age, Vehicle Type, Postcode) drove the price up or down.
2.  **Qualitative Context (RAG)**: It searches internal **Underwriting Guidelines** (PDFs/Text) using **Retrieval Augmented Generation (RAG)** to see if the high price aligns with company policy (e.g., "High risk postcodes must have a 15% loading").
3.  **Historical Precedent**: It searches a database of **Similar Historical Quotes** to check for consistency (e.g., "Do other 30-year-olds in this area pay this much?").

## Key Features & Capabilities
*   **Persona-Driven Analysis**: The system adapts its tone and depth for different users:
    *   *Pricing Analyst*: Technical deep-dive into SHAP values and model logits.
    *   *Underwriter*: Focus on risk rules, guidelines, and policy checks.
    *   *Auditor*: Evidence-based reporting and consistency checks.
*   **Interactive Chat**: Users can ask follow-up questions ("What if the vehicle group is changed?") and get instant, context-aware answers.
*   **Side-by-Side Optimization**: Demonstrates the power of "GenAI Engineering" by running a **Legacy Baseline** (standard LangChain agent) vs. an **Optimized Pipeline** (Parallel, Cached, Engineered) to showcase performance gains.

## Success Criteria
*   **Explainability**: Achieved **77.8% Concept Coverage** (surpassing baseline by ~20%) through rule-aligned RAG.
*   **Performance**: Optimized Architecture restores the latency lead while providing 3x more insight density (**~1.3x Faster** on cold runs).
*   **Accuracy**: Maintains **100% Driver Accuracy** via strict technical validation in the prompt.
