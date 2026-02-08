import json
import asyncio
import os
import sys
import pandas as pd
from datetime import datetime

# Add root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pipelines.optimized_pipeline import run_optimized_pipeline_async
from pipelines.baseline_pipeline import run_baseline_pipeline

def normalize_strict(s):
    return "".join(c for c in s.lower() if c.isalnum())

async def run_pipeline_evaluation(pipeline_type: str = "optimized"):
    """
    Runs pipeline evaluation for a specific architecture and returns results.
    pipeline_type: 'baseline' or 'optimized'
    """
    # Load golden dataset
    dataset_path = 'evaluation/golden_dataset.json'
    if not os.path.exists(dataset_path):
        return {"error": f"Golden dataset not found at {dataset_path}"}
        
    with open(dataset_path, 'r') as f:
        golden_data = json.load(f)
        
    results = []
    print(f"\nStarting {pipeline_type} evaluation of {len(golden_data)} test cases...\n")
    
    for case in golden_data:
        case_id = case['id']
        profile = case['profile']
        query = case['query']
        expected_driver = case['expected_key_driver']
        required_concepts = case['required_concepts']
        
        try:
            start_time = datetime.now()
            
            if pipeline_type == "baseline":
                # Run sync baseline in a thread to keep loop free
                pipeline_res = await asyncio.to_thread(run_baseline_pipeline, profile, query, bypass_cache=True)
            else:
                # Run async optimized
                pipeline_res = await run_optimized_pipeline_async(profile, query, bypass_cache=True)
                
            duration = (datetime.now() - start_time).total_seconds()
            explanation = pipeline_res['explanation']
            
            # Ensure explanation is a string for matching
            if isinstance(explanation, list):
                explanation = "\n".join(explanation)
            elif not isinstance(explanation, str):
                explanation = str(explanation)
            
            # Improved Evaluation Logic (Keyword-based concept matching)
            def normalize_keywords(s):
                return "".join(c for c in s.lower() if c.isalnum() or c.isspace()).split()
            
            explanation_words = set(normalize_keywords(explanation))
            
            # Key Driver Accuracy (Still strictly normalized string match for technical rigor)
            explanation_norm = normalize_strict(explanation)
            driver_match = normalize_strict(expected_driver) in explanation_norm
            
            # Improved Evaluation: G-Eval for Concept Coverage
            # We defer this to the async LLM judge step to be cleaner, 
            # OR we can run it here if we want immediate feedback.
            # Let's run it here since we are already inside an async loop and it replaces the logic.
            
            from evaluation.llm_judge import LLMJudge
            # Initialize judge once outside loop ideally, but for now inside is safer for async ctx or pass it in
            # Actually, let's just initialize it here, overhead is low (connection only)
            judge = LLMJudge()
            
            concept_eval = await judge.evaluate_concepts(explanation, required_concepts)
            if "error" not in concept_eval:
                found_concepts = concept_eval.get("found_concepts", [])
                # Calculate coverage based on semantic match
                concept_coverage = len(found_concepts) / len(required_concepts) if required_concepts else 1.0
            else:
                # Fallback to strict keyword matching if judge fails
                print(f"  [Case {case_id}] Judge failed, falling back into keyword match. Error: {concept_eval['error']}")
                found_concepts = []
                for concept in required_concepts:
                    concept_words = set(normalize_keywords(concept))
                    if concept_words.issubset(explanation_words):
                        found_concepts.append(concept)
                concept_coverage = len(found_concepts) / len(required_concepts)
            
            results.append({
                "case_id": case_id,
                "query": query,
                "explanation": explanation,
                "expected_key_driver": expected_driver,
                "driver_match": driver_match,
                "concept_coverage": concept_coverage,
                "latency": duration,
                "found_concepts": found_concepts,
                "total_concepts": len(required_concepts)
            })
            print(f"  [Case {case_id}] Match: {driver_match}, Coverage: {concept_coverage:.2f}, Latency: {duration:.2f}s")
            
        except Exception as e:
            results.append({
                "case_id": case_id,
                "error": str(e)
            })
            print(f"  [Case {case_id}] ERROR: {str(e)}")
            
    # Aggregate results
    valid_results = [r for r in results if "error" not in r]
    if not valid_results:
        return {"error": f"No valid results for {pipeline_type} pipeline."}
        
    avg_coverage = sum(r['concept_coverage'] for r in valid_results) / len(valid_results)
    driver_accuracy = sum(1 for r in valid_results if r['driver_match']) / len(valid_results)
    avg_latency = sum(r['latency'] for r in valid_results) / len(valid_results)
    
    summary = {
        "pipeline_type": pipeline_type,
        "avg_concept_coverage": avg_coverage,
        "key_driver_accuracy": driver_accuracy,
        "avg_latency": avg_latency
    }
    
    # Save results
    os.makedirs('evaluation/reports', exist_ok=True)
    report_path = f"evaluation/reports/eval_{pipeline_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump({
            "summary": summary,
            "detailed_results": results
        }, f, indent=2)
    
    # Run LLM Judge
    try:
        from evaluation.llm_judge import run_judge_on_report
        await run_judge_on_report(report_path)
    except Exception as e:
        print(f"Could not run LLM judge: {str(e)}")

    return {
        "summary": summary,
        "report_path": report_path
    }

if __name__ == "__main__":
    # If run directly, run both for debugging
    async def run_all():
        print("Benchmarking Baseline...")
        await run_pipeline_evaluation("baseline")
        print("\nBenchmarking Optimized...")
        await run_pipeline_evaluation("optimized")
        
    asyncio.run(run_all())
