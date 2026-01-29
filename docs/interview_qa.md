# Interview Preparation Q&A

### 1. Why is an agent needed here instead of simple RAG?
A simple RAG system just fetches documents based on a query. Here, we need to:
- Interpret numeric ML output (SHAP values).
- Decide *what* to search for (e.g., if Age has the highest SHAP, search for Age guidelines).
- Compare the current quote with historical database records.
An agent (LangGraph) can orchestrate these diverse tool-calling steps in a logical sequence.

### 2. Why is SHAP necessary?
SHAP (SHapley Additive exPlanations) provides a mathematical foundation for feature attribution. It tells us exactly how much the price deviated from the mean for *this specific customer*. This is critical for regulatory "Right to Explanation."

### 3. Why use RAG if the model already predicts the premium?
The ML model predicts based on patterns, but it doesn't "know" the rules. RAG connects those patterns back to the human-written underwriting guidelines. This bridges the gap between statistical probability and corporate policy.

### 4. Why MCP instead of direct Python function calls?
MCP (Model Context Protocol) is an emerging standard for AI-to-Tool communication. Using MCP makes the core "Copilot" logic agnostic to the underlying data source. We could swap SQLite for Snowflake or ChromaDB for Pinecone without changing the agent's core tool definitions.

### 5. How would this scale in a real insurance company?
- **High Volume**: The LightGBM model can handle thousands of inferences per second.
- **Distributed Tools**: MCP servers could be hosted as separate microservices.
- **Monitoring**: We would add telemetry (LangSmith/MLflow) to track how often the agent's explanations align with human underwriter decisions.

### 6. What are the limitations of this prototype?
- **Synthetic Data**: The "true" pricing formula is simpler than real-world actuarial tables.
- **Local LLM**: Ollama is great for privacy, but GPT-4 or Claude 3.5 might offer more nuanced reasoning for complex fringe cases.
- **Similarity Search**: We used basic SQL filtering; real applications would use vector similarity even on the tabular database records.
