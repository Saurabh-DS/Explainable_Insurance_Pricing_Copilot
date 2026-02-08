from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional

@dataclass
class PipelineMetrics:
    total_latency: float = 0.0
    llm_tokens_generated: int = 0
    llm_prompt_tokens: int = 0
    rag_calls: int = 0
    tool_calls: int = 0
    vector_search_latency: float = 0.0
    shap_latency: float = 0.0
    pricing_model_latency: float = 0.0
    llm_latency: float = 0.0
    # specific llm durations (in seconds)
    prompt_eval_duration: float = 0.0
    eval_duration: float = 0.0
    cache_hit: bool = False
    semantic_cache_latency: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class MetricsCollector:
    def __init__(self):
        self.metrics = PipelineMetrics()
        
    def track_latency(self, component: str, duration: float):
        if component == 'total':
            self.metrics.total_latency = duration
        elif component == 'vector_search':
            self.metrics.vector_search_latency += duration
        elif component == 'shap':
            self.metrics.shap_latency += duration
        elif component == 'pricing':
            self.metrics.pricing_model_latency += duration
        elif component == 'llm':
            self.metrics.llm_latency += duration
        elif component == 'semantic_cache':
            self.metrics.semantic_cache_latency += duration
        elif component == 'similarity':
             # Mapping similarity tool latency to vector search or its own, 
             # but user asked for 'vector search time'. 
             # Similar quotes uses SQL, Guidelines uses Chroma (Vector).
             pass

    def track_tokens(self, prompt: int, generated: int):
        self.metrics.llm_prompt_tokens += prompt
        self.metrics.llm_tokens_generated += generated

    def track_llm_stats(self, prompt_duration_ns: int, eval_duration_ns: int):
        # Convert nanoseconds to seconds
        self.metrics.prompt_eval_duration = prompt_duration_ns / 1_000_000_000
        self.metrics.eval_duration = eval_duration_ns / 1_000_000_000

    def increment_counter(self, counter: str, value: int = 1):
        if counter == 'rag_calls':
            self.metrics.rag_calls += value
        elif counter == 'tool_calls':
            self.metrics.tool_calls += value

    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics.to_dict()
