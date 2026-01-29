from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent.graph import run_agent
import uvicorn
import sys
import os
import time
import uuid

# Ensure parent directory is in path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = FastAPI(title="Insurance Pricing Copilot API")

class QuoteProfile(BaseModel):
    age: int
    postcode_risk: float
    vehicle_group: int
    claims_count: int
    ncb_years: int

@app.get("/")
def read_root():
    return {"status": "online", "message": "Insurance Pricing Copilot API is ready."}

@app.post("/explain")
async def explain_premium(profile: QuoteProfile):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    profile_dict = profile.model_dump()
    
    try:
        # Run agent
        result = run_agent(profile_dict)
        total_latency = (time.time() - start_time) * 1000
        
        return {
            "explanation": result['explanation'],
            "request_id": request_id,
            "latency_ms": total_latency,
            "metrics": result['metadata']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
