from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent.graph import run_agent
import uvicorn
import os
import sys

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
    try:
        # Convert Pydantic model to dict
        profile_dict = profile.model_dump()
        explanation = run_agent(profile_dict)
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
