import sys
import os
import json
import time
import asyncio
import functools
import shap
import pandas as pd
import numpy as np
from chromadb.utils import embedding_functions
from rank_bm25 import BM25Okapi
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage

# Add root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pricing_model.predict import get_model_data
from mcp_server.server import get_similar_quotes, search_guidelines
from observability.metrics import MetricsCollector
from observability.timer import measure_time

# --- Optimization 1: Global Caching for Model & Explainer ---
_PRICING_CACHE = None

# --- Optimization Bonus: Global Semantic Response Cache ---
# Structure: { profile_hash: [ {'embedding': np.array, 'result': dict, 'query': str} ] }
_RESPONSE_CACHE = {}
_EMBEDDING_FUNC = embedding_functions.DefaultEmbeddingFunction()

def get_cached_pricing_components():
    global _PRICING_CACHE
    if _PRICING_CACHE is None:
        data = get_model_data()
        model = data['model']
        explainer = shap.TreeExplainer(model)
        _PRICING_CACHE = (model, data['features'], explainer)
    return _PRICING_CACHE

def run_pricing_optimized(profile: dict):
    # Uses cached explainer to avoid re-initialization overhead (Optimization: SHAP caching)
    model, features, explainer = get_cached_pricing_components()
    
    df = pd.DataFrame([profile])
    # Ensure columns match expected features
    if not all(col in df.columns for col in features):
        print(f"DEBUG: Missing features. Profile: {list(df.columns)}, Expected: {features}")
    
    df = df[features]
    premium = model.predict(df)[0]
    
    # SHAP calculation is faster if explainer is reused? 
    # TreeExplainer init is expensive. Computing shap_values is separate.
    shap_values = explainer.shap_values(df)
    
    if isinstance(shap_values, list):
        shap_vals = shap_values[0][0]
    else:
        shap_vals = shap_values[0]
        
    explanation = {}
    for i, feature in enumerate(features):
        explanation[feature] = float(shap_vals[i])
        
    return {
        "predicted_premium": round(float(premium), 2),
        "shap_values": explanation
    }

# --- Optimization 2: Global Persistent Chroma Client ---
_CHROMA_CLIENT = None
_CHROMA_COLLECTION = None

def get_underwriting_collection():
    global _CHROMA_CLIENT, _CHROMA_COLLECTION
    if _CHROMA_COLLECTION is None:
        import chromadb
        persist_directory = "database/chroma_db"
        _CHROMA_CLIENT = chromadb.PersistentClient(path=persist_directory)
        _CHROMA_COLLECTION = _CHROMA_CLIENT.get_collection(
            name="underwriting_guidelines",
            embedding_function=embedding_functions.DefaultEmbeddingFunction()
        )
    return _CHROMA_COLLECTION

def search_guidelines_hybrid(query: str, features: list, n_results: int = 3):
    """
    Hybrid Search: Vector Search + BM25 Reranking
    """
    collection = get_underwriting_collection()
    
    # 1. Vector Search (Semantic)
    # Search for user query AND top features
    search_queries = [query] + features
    vector_results = collection.query(
        query_texts=search_queries,
        n_results=n_results
    )
    
    # Deduplicate and flatten
    unique_docs = {} # content -> metadata
    
    # Process vector results
    for i, docs in enumerate(vector_results['documents']):
        for j, doc in enumerate(docs):
            if doc not in unique_docs:
                unique_docs[doc] = vector_results['metadatas'][i][j]

    # Quick return if no docs
    if not unique_docs:
        return ""
        
    docs_list = list(unique_docs.keys())
    
    # 2. BM25 Ranking (Keyword)
    # Tokenize corpus
    tokenized_corpus = [doc.split(" ") for doc in docs_list]
    bm25 = BM25Okapi(tokenized_corpus)
    
    # Score against query
    tokenized_query = query.split(" ")
    doc_scores = bm25.get_scores(tokenized_query)
    
    # 3. Simple Reranking/Filtering
    # Sort by score
    scored_docs = sorted(zip(docs_list, doc_scores, [unique_docs[d] for d in docs_list]), key=lambda x: x[1], reverse=True)
    
    # Return top K (e.g., top 3 most relevant chunks)
    top_k = scored_docs[:3]
    
    formatted_results = []
    for doc, score, meta in top_k:
        source_info = f"[Source: {meta.get('source', 'unknown')}]"
        formatted_results.append(f"{source_info}\n{doc}")
        
    return "\n---\n".join(formatted_results)

async def timed_task(func, *args, **kwargs):
    start = time.time()
    res = await asyncio.to_thread(func, *args, **kwargs)
    duration = time.time() - start
    return res, duration

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def check_semantic_cache_sync(profile_hash, query_embedding, threshold=0.85):
    if profile_hash not in _RESPONSE_CACHE:
        return None
    for entry in _RESPONSE_CACHE[profile_hash]:
        if cosine_similarity(query_embedding, entry['embedding']) > threshold:
            return entry['result']
    return None

async def run_optimized_pipeline_async(profile: dict, query: str = "Explain premium calculation briefly.", bypass_cache: bool = False):
    collector = MetricsCollector()
    total_start = time.time()
    profile_hash = hash(str(profile))
    
    # --- Optimization 4: Extreme Parallelization ---
    # Executes Guideline Search, Pricing, and Similar Quotes in a single concurrent gather.
    # To enable this, we search for all relevant feature keywords concurrently with pricing.
    
    t_parallel_start = time.time()
    all_feature_keywords = ["age", "postcode_risk", "vehicle_group", "claims_count", "ncb_years", "years_experience"]
    
    task_embedding = asyncio.to_thread(_EMBEDDING_FUNC, [query])
    task_pricing = timed_task(run_pricing_optimized, profile)
    task_similar = timed_task(get_similar_quotes, profile)
    task_guidelines = asyncio.to_thread(search_guidelines_hybrid, query, all_feature_keywords)
    
    # Run all non-dependent tasks in parallel
    emb_res, (pricing_res, pricing_time), (similar_res, similar_time), guidelines_combined = await asyncio.gather(
        task_embedding, task_pricing, task_similar, task_guidelines
    )
    query_embedding = emb_res[0]
    
    # Now check semantic cache AFTER we have the embedding
    t_sem_start = time.time()
    cached_result = None if bypass_cache else check_semantic_cache_sync(profile_hash, query_embedding)
    actual_check_time = time.time() - t_sem_start
    
    if cached_result:
        cached_metrics = cached_result['metrics'].copy()
        cached_metrics['cache_hit'] = True
        cached_metrics['total_latency'] = time.time() - total_start
        cached_metrics['semantic_cache_latency'] = actual_check_time
        cached_metrics['pricing_model_latency'] = 0.0
        cached_metrics['vector_search_latency'] = 0.0
        cached_metrics['llm_latency'] = 0.0
        return {"explanation": cached_result['explanation'], "metrics": cached_metrics}

    collector.track_latency('semantic_cache', actual_check_time)
    collector.track_latency('pricing', pricing_time)
    collector.track_latency('vector_search', time.time() - t_parallel_start) 
    collector.increment_counter('rag_calls', 1)
    
    # Extract SHAP values for prompt construction
    shap_vals = pricing_res['shap_values']
    
    # --- Optimization 5 & 6: Feature-Anchored Structured Prompting ---
    top_features_list = sorted(shap_vals.items(), key=lambda x: abs(x[1]), reverse=True)
    # FIX: Remove '£' prefix for SHAP values as they are not currency, but importance/logit scores
    # Create simplified contribution context with "Impact Score"
    contribution_context = "\n".join([f"- {f}: Impact Score {'+' if v > 0 else ''}{v:.2f}" for f, v in top_features_list])
    top_feature = top_features_list[0][0]

    system_prompt = f"""Role: Expert Insurance Pricing Analyst.
    Output a COMPACT ANALYST REPORT for the premium (£{pricing_res['predicted_premium']}).

    Context:
    - Customer: {profile}
    - Drivers/Scores: {contribution_context}
    - Rules: {guidelines_combined}

    Instructions:
    1. Output a high-density Analyst Report explaining the premium.
    2. Analyze the Primary Driver ({top_feature}) and how it aligns with Policy Rules.
    3. Detail all other significant secondary factors (Age, Claims, NCB, etc.) and include their exact names in parentheses, e.g. "high risk (postcode_risk)".
    4. Cite specific rules (e.g. "Source: vehicle_group.txt") for all major factors.
    5. Stay professional but move directly into the analysis to save time.

    Constraints:
    - Tone: Professional Analyst. Terminology: 'Risk Profile', 'Claims History', 'NCB'.
    - Formatting: NO bullet points. FULL sentences only. 
    - Max Length: 250 words maximum.

    Verification:
    Primary Driver: {top_feature}
    """
    
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    llm = ChatOllama(
        model="llama3", 
        temperature=0,
        base_url=ollama_url,
        num_predict=250, # Sufficient for depth, but prevents rambling
    )
    
    t_llm_start = time.time()
    # invoke LLM
    response = await llm.ainvoke([SystemMessage(content=system_prompt)])
    t_llm_duration = time.time() - t_llm_start
    
    collector.track_latency('llm', t_llm_duration)
    collector.increment_counter('tool_calls', 3) # Pricing, Similar, Guidelines

    # --- Optimization 7: Simplified Parsing (Reasoning + Explanation) ---
    content = response.content.strip()
    explanation_text = content
    
    # Try to strip "Reasoning:" prefix to keep explanation clean for UI if needed, 
    # but keeping it might be better for "Explainability". 
    # Let's keep the full text as it adds confidence.
    
    parsed_res = {"primary_driver": top_feature} # Inferred from SHAP

    # Extract tokens for optimized pipeline
    if hasattr(response, 'response_metadata'):
        meta = response.response_metadata
        collector.track_tokens(prompt=meta.get('prompt_eval_count', 0), generated=meta.get('eval_count', 0))
        collector.track_llm_stats(
            prompt_duration_ns=meta.get('prompt_eval_duration', 0),
            eval_duration_ns=meta.get('eval_duration', 0)
        )
    
    # Total Latency
    collector.track_latency('total', time.time() - total_start)

    result = {
        "explanation": explanation_text,
        "metrics": collector.get_metrics(),
        "metadata": parsed_res
    }
    
    # Populate Sematic Cache
    if profile_hash not in _RESPONSE_CACHE:
        _RESPONSE_CACHE[profile_hash] = []
    
    _RESPONSE_CACHE[profile_hash].append({
        'embedding': query_embedding,
        'result': result,
        'query': query
    })
    
    return result

def run_optimized_pipeline(profile: dict, query: str = "Explain premium calculation briefly.", bypass_cache: bool = False):
    return asyncio.run(run_optimized_pipeline_async(profile, query, bypass_cache))
