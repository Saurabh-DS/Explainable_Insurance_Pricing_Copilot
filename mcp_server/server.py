from mcp.server.fastmcp import FastMCP
import sqlite3
import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
import sys
import os

# Add parent directory to path so we can import pricing_model.predict
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pricing_model.predict import predict_premium

# Initialize MCP Server
mcp = FastMCP("InsurancePricing")

# --- Tools ---

@mcp.tool()
def search_guidelines(query: str) -> str:
    """
    Search underwriting guidelines in ChromaDB for a given query.
    Useful for explaining policy rules related to age, postcode, vehicle, etc.
    """
    persist_directory = "database/chroma_db"
    client = chromadb.PersistentClient(path=persist_directory)
    collection = client.get_collection(
        name="underwriting_guidelines",
        embedding_function=embedding_functions.DefaultEmbeddingFunction()
    )
    
    results = collection.query(
        query_texts=[query],
        n_results=2
    )
    
    docs = results['documents'][0]
    return "\n---\n".join(docs)

@mcp.tool()
def run_pricing_model(profile: dict) -> dict:
    """
    Run the ML pricing model for a given customer profile.
    Profile should contain: age, postcode_risk, vehicle_group, claims_count, ncb_years.
    Returns predicted premium and SHAP values explaining the prediction.
    """
    return predict_premium(profile)

@mcp.tool()
def get_similar_quotes(profile: dict, limit: int = 5) -> str:
    """
    Search the SQLite database for quotes with similar profiles to justify pricing.
    Uses basic filtering on age and vehicle group for 'similarity' in this prototype.
    """
    conn = sqlite3.connect('database/quotes.db')
    
    # Simple similarity: match age range and vehicle group range
    age = profile.get('age', 30)
    vg = profile.get('vehicle_group', 20)
    
    query = f"""
    SELECT * FROM quotes 
    WHERE age BETWEEN {age-2} AND {age+2}
    AND vehicle_group BETWEEN {vg-3} AND {vg+3}
    LIMIT {limit}
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        return "No similar quotes found in the database."
    
    return df.to_markdown(index=False)

if __name__ == "__main__":
    mcp.run()
