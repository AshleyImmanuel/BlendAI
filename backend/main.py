import logging
from typing import Optional
import sys
import os
import time
from collections import defaultdict
from fastapi import FastAPI, HTTPException, Request  # type: ignore # noqa: F401
from pydantic import BaseModel  # type: ignore # noqa: F401
import uvicorn  # type: ignore # noqa: F401

# --- LOGGING CONFIGURATION ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), "blendai_swarm.log"))
    ]
)
logger = logging.getLogger("BlendAI")

# Ensure the backend directory is in the path for internal imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.swarm_manager import SwarmManager  # type: ignore # noqa: F401
from utils.persistent_memory import persistent_memory  # type: ignore # noqa: F401

app = FastAPI(
    title="BlendAI Swarm Backend v1.7.0",
    description="Backend API for the Autonomous BlendAI Swarm. Features safety guards, injection resistance, and rate limiting."
)

# --- SECURITY: RATE LIMITER ---
class RateLimiter:
    def __init__(self, limit_per_minute: int = 10):
        self.limit = limit_per_minute
        self.history = defaultdict(list)

    def check_rate_limit(self, session_id: str):
        now = time.time()
        # Filter history to keep only the last 60 seconds
        self.history[session_id] = [t for t in self.history[session_id] if t > now - 60]
        if len(self.history[session_id]) >= self.limit:
            return False
        self.history[session_id].append(now)
        return True

rate_limiter = RateLimiter(limit_per_minute=10)

class RunRequest(BaseModel):
    prompt: str
    api_key: str
    session_id: str = "default_user"
    model: str = "gpt-4o"
    base_url: Optional[str] = None

class ResetRequest(BaseModel):
    session_id: str = "default_user"

@app.get("/")
def root():
    return {"message": "BlendAI Swarm is Online"}

@app.post("/run")
def run_ai(request: RunRequest):
    """
    Triggers the Autonomous Swarm logic with security guards.
    """
    logger.info(f"Received mission request for session: {request.session_id}")
    
    # 1. Rate Limiting Check
    if not rate_limiter.check_rate_limit(request.session_id):
        logger.warning(f"Rate limit exceeded for session: {request.session_id}")
        raise HTTPException(
            status_code=429, 
            detail="Rate limit exceeded (10 requests/min). Please slow down to protect your API budget."
        )

    # 2. Key Verification
    if not request.api_key or len(request.api_key) < 5:
        logger.error("API call rejected: Missing or invalid key.")
        raise HTTPException(status_code=400, detail="Valid API Key required.")
    
    if not request.prompt or not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    
    try:
        swarm = SwarmManager(
            api_key=request.api_key,
            model=request.model,
            base_url=request.base_url
        )
        
        # 3. Resolve through iterative swarm
        result = swarm.resolve(request.session_id, request.prompt)
        
        return {
            "code": result["code"],
            "critic": result["report"],
            "new_skill": result["new_skill"]
        }
        
    except Exception as e:
        # 4. Error Scrubbing: Ensure no API keys are leaked in tracebacks
        error_msg = str(e)
        if request.api_key in error_msg:
            error_msg = error_msg.replace(request.api_key, "[REDACTED]")
        
        logger.error(f"Internal Swarm Error: {error_msg}")
        raise HTTPException(status_code=500, detail="Internal Swarm Error. Key has been redacted for safety.")

@app.post("/reset")
def reset_memory(request: ResetRequest):
    """
    Clears the persistent session history for the specified user.
    """
    logger.info(f"Resetting history for session: {request.session_id}")
    persistent_memory.clear_session(request.session_id)
    return {"status": "BlendAI history cleared for session", "session_id": request.session_id}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
