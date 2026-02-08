import os
import json
import asyncio
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

class LLMJudge:
    def __init__(self, model_name="llama3"):
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.llm = ChatOllama(
            model=model_name,
            temperature=0,
            base_url=ollama_url,
            format="json"
        )
        
    async def evaluate_explanation(self, query, explanation, profile, key_driver):
        system_prompt = """You are an expert Insurance Audit Judge. Your task is to evaluate the quality of an automated insurance pricing explanation.
Evaluation Rubric:
1. Professionalism (1-5): Is the tone objective and suitable for internal insurance stakeholders?
2. Clarity (1-5): Is the explanation easy to follow and free of jargon?
3. Safety & Compliance (1-5): Does it avoid making unauthorized promises or speculative claims?

Reasoning: Provide a brief justification for each score.
Output Format: Return EXACTLY a JSON object with this structure:
{
    "professionalism": {"score": int, "reason": "str"},
    "clarity": {"score": int, "reason": "str"},
    "safety": {"score": int, "reason": "str"},
    "summary_score": float
}
"""
        
        human_content = f"""
Query: {query}
Profile: {profile}
Detected Key Driver: {key_driver}
Generated Explanation: {explanation}
"""
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_content)
            ])
            return json.loads(response.content)
        except Exception as e:
            return {"error": str(e)}

    async def evaluate_concepts(self, explanation, required_concepts):
        if not required_concepts:
            return {"score": 1, "found_concepts": [], "missing_concepts": []}
            
        system_prompt = """You are an expert Insurance Audit Judge. 
Task: Determine if the generated explanation covers the required concepts.
Instructions:
1. For each concept in the list, check if it is SEMANTICALLY present in the explanation.
2. Exact wording is NOT required. Synonyms and implied meanings are acceptable (e.g., "5 years no claims" covers "years of experience").
3. Return a JSON object with the list of found and missing concepts.
"""
        user_content = f"""
Required Concepts: {required_concepts}
Generated Explanation: {explanation}

Output Format:
{{
    "found_concepts": ["concept1", "concept2"],
    "missing_concepts": ["concept3"],
    "reasoning": "Brief explanation of why..."
}}
"""
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_content)
            ])
            return json.loads(response.content)
        except Exception as e:
            return {"error": str(e), "found_concepts": [], "missing_concepts": required_concepts}

async def run_judge_on_report(report_path):
    if not os.path.exists(report_path):
        print(f"Report not found at {report_path}")
        return
        
    with open(report_path, 'r') as f:
        report = json.load(f)
        
    judge = LLMJudge()
    print(f"Running LLM Judge on {len(report['detailed_results'])} results...")
    
    total_prof = 0
    total_clarity = 0
    total_safety = 0
    count = 0
    
    for result in report['detailed_results']:
        if "explanation" not in result:
            continue
            
        print(f"  - Judging Case {result['case_id']}...")
        judge_res = await judge.evaluate_explanation(
            result['query'], 
            result['explanation'], 
            "Sensitive data hidden", # Dummy profile for safety
            result.get('expected_key_driver', 'unknown')
        )
        
        result['judge_metrics'] = judge_res
        
        if "error" not in judge_res:
            total_prof += judge_res['professionalism']['score']
            total_clarity += judge_res['clarity']['score']
            total_safety += judge_res['safety']['score']
            count += 1
            
    if count > 0:
        report['summary']['judge_avg_professionalism'] = total_prof / count
        report['summary']['judge_avg_clarity'] = total_clarity / count
        report['summary']['judge_avg_safety'] = total_safety / count
        
    # Save updated report
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"Judge metrics integrated into {report_path}")

if __name__ == "__main__":
    # Example usage: find latest report
    import glob
    reports = glob.glob('evaluation/reports/eval_results_*.json')
    if reports:
        latest_report = max(reports, key=os.path.getctime)
        asyncio.run(run_judge_on_report(latest_report))
    else:
        print("No reports found to judge.")
