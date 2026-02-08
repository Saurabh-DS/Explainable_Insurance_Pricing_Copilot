# User Interface Design Concepts

The application interface is built with `Streamlit` but designed with **Product Principles**, focusing on Trust, Transparency, and Efficiency.

## 1. Persona-Driven Interaction

The "One Size Fits All" approach is avoided in complex domains like insurance. The experience is tailored for three distinct internal personas:

*   **Underwriter**:
    *   *Needs*: Risk assessment, policy adherence checks.
    *   *UI Focus*: Highlights "Red Flag" guidelines and risk factors.
*   **Pricing Analyst**:
    *   *Needs*: Mathematical justification, feature impact.
    *   *UI Focus*: Detailed SHAP value charts and model probability scores.
*   **Compliance Auditor**:
    *   *Needs*: Consistency, traceability, "Why".
    *   *UI Focus*: Links to specific policy documents and historical quote variance.

*Selecting a persona in the sidebar dynamically alters the System Prompt instructions sent to the LLM.*

## 2. Comparison Mode (A/B View)

To build trust in the "Optimized" pipeline, it is rendered alongside the "Baseline" implementation.
*   **Split Layout**: Two distinct columns allow for direct text comparison (Quality check).
*   **Unified Telemetry**: A single table below the chat unifies the performance data (Speed check).
*   **Visual Logic**:
    *    **Clean Labels**: Distinct labeling for Baseline vs. Optimized (Latency Dominant).
    *    **Notification Badges**: "INSTANT CACHE HIT" notifications provide feedback when Semantic Caching engages.

## 3. Trust Through Transparency

The framework adheres to the **"Glass Box"** design philosophy:
*   **Mathematical Transparency**: Raw Premium (£) and SHAP contribution lists are displayed alongside the summarized analysis.
*   **Show the Source**: RAG responses ideally cite the specific guideline document used (e.g., *Source: young_driver_policy_2024.txt*).
*   **Show the Cost**: The token counts and latency metrics ensure the user understands the computational cost of their query.
