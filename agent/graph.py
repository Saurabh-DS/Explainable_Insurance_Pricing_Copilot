from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
import sys
import os
import time

# Import tools directly for convenience 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mcp_server.server import search_guidelines, run_pricing_model, get_similar_quotes

# Reducer for merging metadata dictionaries
def merge_metadata(left: dict, right: dict) -> dict:
    return {**left, **right}

# Define the state
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "The messages in the conversation"]
    profile: dict
    pricing_data: dict
    guidelines: str
    similar_quotes: str
    explanation: str
    user_query: str 
    # Telemetry storage in state with a merge reducer to handle concurrent updates
    metadata: Annotated[dict, merge_metadata]

# Initialize the LLM
ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
llm = ChatOllama(
    model="llama3", 
    temperature=0,
    base_url=ollama_url
)

# --- Nodes ---

def call_pricing_tool(state: AgentState):
    start_time = time.time()
    profile = state['profile']
    pricing_data = run_pricing_model(profile)
    latency = (time.time() - start_time) * 1000
    return {
        "pricing_data": pricing_data,
        "metadata": {"pricing_latency": latency}
    }

def call_guideline_tool(state: AgentState):
    start_time = time.time()
    # Determine what to search for based on significant SHAP values
    shap = state['pricing_data']['shap_values']
    # Find the most impactful feature
    top_feature = max(shap, key=lambda k: abs(shap[k]))
    
    # Check if we should use the Naive Baseline tool
    use_baseline = state.get('metadata', {}).get('use_baseline', False)
    
    if use_baseline:
        # Import the naive tool dynamically or ensure it is available
        from mcp_server.server import search_guidelines_baseline
        guidelines = search_guidelines_baseline(top_feature)
    else:
        guidelines = search_guidelines(top_feature)
        
    latency = (time.time() - start_time) * 1000
    return {
        "guidelines": guidelines,
        "metadata": {"guidelines_latency": latency}
    }

def call_similarity_tool(state: AgentState):
    start_time = time.time()
    profile = state['profile']
    similar_quotes = get_similar_quotes(profile)
    latency = (time.time() - start_time) * 1000
    return {
        "similar_quotes": similar_quotes,
        "metadata": {"similarity_latency": latency}
    }

def generate_explanation(state: AgentState):
    start_time = time.time()
    profile = state['profile']
    pricing = state['pricing_data']
    guidelines = state['guidelines']
    similar_docs = state['similar_quotes']
    user_query = state.get('user_query', "Please explain my insurance premium.")
    
    system_prompt = """
    You are an Expert AI Insurance Pricing Copilot. Your goal is to assist Pricing Analysts and Underwriters in understanding model decisions.
    
    Context provided:
    1. Customer Profile: {profile}
    2. Predicted Premium: {premium}
    3. SHAP values (Feature Importance): {shap}
    4. Relevant Underwriting Guidelines: {guidelines}
    5. Similar Historical Quotes: {similar_docs}
    
    Instructions:
    - Provide a detailed technical explanation.
    - Explicitly reference SHAP values to explain the model's 'why'.
    - Verify alignment with underwriting guidelines.
    - Confirm consistency with historical quotes.
    - Specificly address the User's Query.
    - DO NOT use any emojis in your response.
    """
    
    prompt = system_prompt.format(
        profile=profile,
        premium=pricing['predicted_premium'],
        shap=pricing['shap_values'],
        guidelines=guidelines,
        similar_docs=similar_docs
    )
    
    response = llm.invoke([SystemMessage(content=prompt), HumanMessage(content=user_query)])
    latency = (time.time() - start_time) * 1000
    
    # Extract token usage
    prompt_tokens = 0
    completion_tokens = 0
    prompt_eval_duration = 0
    eval_duration = 0
    
    if hasattr(response, 'response_metadata'):
        meta = response.response_metadata
        prompt_tokens = meta.get('prompt_eval_count', 0)
        completion_tokens = meta.get('eval_count', 0)
        prompt_eval_duration = meta.get('prompt_eval_duration', 0)
        eval_duration = meta.get('eval_duration', 0)
        
    return {
        "explanation": response.content,
        "metadata": {
            "llm_latency": latency,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "prompt_eval_duration": prompt_eval_duration,
            "eval_duration": eval_duration
        }
    }

# --- Construction ---

builder = StateGraph(AgentState)

builder.add_node("pricing", call_pricing_tool)
builder.add_node("guidelines", call_guideline_tool)
builder.add_node("similarity", call_similarity_tool)
builder.add_node("explainer", generate_explanation)

builder.add_edge(START, "pricing")
builder.add_edge("pricing", "guidelines")
builder.add_edge("pricing", "similarity")
builder.add_edge("guidelines", "explainer")
builder.add_edge("similarity", "explainer")
builder.add_edge("explainer", END)

graph = builder.compile()

def run_agent(profile: dict, query: str = "Please explain my insurance premium.", use_baseline: bool = False):
    initial_state = {
        "messages": [],
        "profile": profile,
        "pricing_data": {},
        "guidelines": "",
        "similar_quotes": "",
        "explanation": "",
        "user_query": query,
        "metadata": {"use_baseline": use_baseline}
    }
    result = graph.invoke(initial_state)
    return {
        "explanation": result['explanation'],
        "metadata": result['metadata']
    }
