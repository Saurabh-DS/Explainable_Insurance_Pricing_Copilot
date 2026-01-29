from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
import sys
import os

# Import tools directly for convenience in the same process, 
# though in a real MCP setup they would be called via the MCP protocol.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mcp_server.server import search_guidelines, run_pricing_model, get_similar_quotes

import time

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
    # Telemetry storage in state with a merge reducer to handle concurrent updates
    metadata: Annotated[dict, merge_metadata]

# Initialize the LLM with environment variable support for base_url
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
    
    system_prompt = """
    You are an AI Insurance Underwriter Assistant. Your goal is to explain the calculated insurance premium to a customer or a junior underwriter.
    
    Context provided:
    1. Customer Profile: {profile}
    2. Predicted Premium: {premium}
    3. SHAP values (Feature Importance): {shap}
    4. Relevant Underwriting Guidelines: {guidelines}
    5. Similar Historical Quotes: {similar_docs}
    
    Instructions:
    - Be professional and transparent.
    - Explain WHY the premium is what it is, citing specific features and guidelines.
    - Mention if the premium is higher or lower than similar historical quotes.
    - Use the SHAP values to quantify the impact of each feature.
    """
    
    prompt = system_prompt.format(
        profile=profile,
        premium=pricing['predicted_premium'],
        shap=pricing['shap_values'],
        guidelines=guidelines,
        similar_docs=similar_docs
    )
    
    response = llm.invoke([SystemMessage(content=prompt), HumanMessage(content="Please explain my insurance premium.")])
    latency = (time.time() - start_time) * 1000
    return {
        "explanation": response.content,
        "metadata": {"llm_latency": latency}
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

def run_agent(profile: dict):
    initial_state = {
        "messages": [],
        "profile": profile,
        "pricing_data": {},
        "guidelines": "",
        "similar_quotes": "",
        "explanation": "",
        "metadata": {}
    }
    result = graph.invoke(initial_state)
    return {
        "explanation": result['explanation'],
        "metadata": result['metadata']
    }
