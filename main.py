import os
import sys
import uvicorn
from fastapi import FastAPI, Body

# 1. FORCE THE PATH - Do this before ANY other imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# 2. GLOBAL IMPORTS - Move these out of the function to prevent "circles"
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from market_analyst.agent import root_agent 

app = FastAPI()

@app.get("/")
async def health_check():
    return {"status": "alive"}

@app.post("/handle")
async def handle_request(text: str = Body(..., embed=True)):
    try:
        # 3. Create the session and runner using the global imports
        session_service = InMemorySessionService()
        runner = Runner(agent=root_agent, session_service=session_service)
        
        # 4. Execute
        result = await runner.run_debug(text)
        return {"output": result.text}

    except Exception as e:
        # This will catch specific DB or Module errors
        return {"error": str(e), "status": "failed"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
