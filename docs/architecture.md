# System Architecture In-Depth

## 1. Data Flow
1. **Input**: A dictionary representing a customer profile (age, postcode risk, etc.).
2. **Prediction**: The `Pricing Model` (LightGBM) computes the premium. 
3. **Attribution**: The `SHAP TreeExplainer` identifies which features pushed the price up or down.
4. **Contextualization**:
   - The `MCP Server` facilitates searches into:
     - **ChromaDB**: Finding human-readable underwriting rules that justify the ML behavior.
     - **SQLite**: Finding similar historical quotes to ground the price in reality.
5. **Synthesis**: `LangGraph` orchestrates these tool calls and feeds the data into `Ollama (Llama3)` to generate a natural language explanation.

## 2. Why this Stack?

### Why ML Model instead of Rules?
Traditional GLMs (Generalized Linear Models) are standard in insurance but struggle with non-linear interactions. LightGBM handles complex patterns better, and SHAP brings back the transparency usually lost in ML.

### Why Agent Orchestration?
Explaining a price requires multi-step reasoning: "The price is high because of X, which is justified by guideline Y, and we see similar prices in cases Z." An agent handles this dependency better than a simple prompt.

### Why MCP?
The Model Context Protocol keeps the tools decoupled. In a real insurer, the pricing engine, the document store, and the customer database might be owned by different teams. MCP provides a standardized way for an AI to interact with them.

### Why RAG for Governance?
Insurance is highly regulated. You cannot just say "because the AI said so." RAG allows the model to cite specific, approved policy documents, ensuring the explanation stays within the bounds of corporate governance.
