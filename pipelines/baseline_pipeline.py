import sys
import os
import time

# Add root directory to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.graph import run_agent
from observability.metrics import MetricsCollector
from observability.timer import measure_time

def run_baseline_pipeline(profile: dict, query: str = "Please explain my insurance premium.", bypass_cache: bool = False):
    collector = MetricsCollector()
    
    with measure_time() as total_timer:
        # Run the existing agent with naive baseline configuration
        result = run_agent(profile, query, use_baseline=True)
    
    # Capture Total Latency
    collector.track_latency('total', total_timer.duration)
    
    # Extract metadata from agent result
    metadata = result.get('metadata', {})
    
    # Map agent metadata to standardized metrics
    # graph.py provides latencies in milliseconds
    
    if 'pricing_latency' in metadata:
        # This covers Model Prediction + SHAP
        # Since we can't split it in baseline without code changes, we assign it to pricing_model_latency
        duration_sec = metadata['pricing_latency'] / 1000.0
        collector.track_latency('pricing', duration_sec)
        # We also attribute it to SHAP roughly for the sake of comparison if user wants to see SHAP time
        # But accurately it's combined. We will leave SHAP as 0 or equal to pricing for now?
        # Let's just track pricing.
        
    if 'guidelines_latency' in metadata:
        # This is RAG (Vector Search)
        duration_sec = metadata['guidelines_latency'] / 1000.0
        collector.track_latency('vector_search', duration_sec)
        collector.increment_counter('rag_calls', 1) 

    if 'similarity_latency' in metadata:
        # SQL search
        pass

    if 'llm_latency' in metadata:
         duration_sec = metadata['llm_latency'] / 1000.0
         collector.track_latency('llm', duration_sec)

    if 'prompt_tokens' in metadata:
        collector.track_tokens(prompt=metadata['prompt_tokens'], generated=metadata.get('completion_tokens', 0))

    if 'prompt_eval_duration' in metadata:
        collector.track_llm_stats(
            prompt_duration_ns=metadata.get('prompt_eval_duration', 0),
            eval_duration_ns=metadata.get('eval_duration', 0)
        )

    # Baseline agent always makes 3 tool calls (pricing, guidelines, similarity)
    collector.increment_counter('tool_calls', 3)
    
    # Baseline prompt size is roughly constant + profile text. 
    # We don't have exact prompt size in metadata yet.
    # We will approximate or leave 0 until Step 5.
    
    return {
        "explanation": result['explanation'],
        "metrics": collector.get_metrics()
    }
