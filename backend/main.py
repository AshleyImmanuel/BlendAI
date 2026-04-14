import logging
from typing import Optional, List, Dict
import sys
import os
import time
import asyncio
from collections import defaultdict
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect  # type: ignore # noqa: F401
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

# --- WEBSOCKET CONNECTION MANAGER ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id].append(websocket)
        logger.info(f"WebSocket connected: {session_id}")

    def disconnect(self, websocket: WebSocket, session_id: str):
        if websocket in self.active_connections[session_id]:
            self.active_connections[session_id].remove(websocket)
            logger.info(f"WebSocket disconnected: {session_id}")

    async def broadcast(self, session_id: str, message: dict):
        for connection in self.active_connections[session_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send WS message: {e}")

manager = ConnectionManager()

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
    scene_summary: Optional[str] = None

class ResetRequest(BaseModel):
    session_id: str = "default_user"

@app.get("/")
def root():
    return {"message": "BlendAI Swarm is Online"}

@app.websocket("/ws/progress/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)

@app.post("/run")
async def run_ai(request: RunRequest):
    """
    Triggers the Autonomous Swarm logic with security guards and progress reporting.
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
        # Define the callback for the swarm manager
        def progress_callback(status):
            # We need to bridge synchronous swarm to asynchronous websocket
            # FastAPI's background tasks or looping through connections
            loop = asyncio.get_event_loop()
            asyncio.run_coroutine_threadsafe(
                manager.broadcast(request.session_id, status),
                loop
            )

        swarm = SwarmManager(
            api_key=request.api_key,
            model=request.model,
            base_url=request.base_url
        )
        
        # 3. Resolve through iterative swarm (run in thread to avoid blocking loop)
        # However, for simplicity in this setup, we call it directly if it's fast 
        # but better to run in threadpool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            swarm.resolve, 
            request.session_id, 
            request.prompt, 
            request.scene_summary,
            progress_callback
        )
        
        return {
            "code": result["code"],
            "critic": result["report"],
            "new_skill": result["new_skill"],
            "status": result.get("status", "OK"),
            "reason": result.get("reason", "")
        }
        
    except Exception as e:
        # 4. Error Scrubbing
        error_msg = str(e)
        if request.api_key in error_msg:
            error_msg = error_msg.replace(request.api_key, "[REDACTED]")
        
        logger.error(f"Internal Swarm Error: {error_msg}")
        raise HTTPException(status_code=500, detail="Internal Swarm Error. Key has been redacted for safety.")

# --- EXECUTION BRIDGE (UI -> Blender) ---
pending_execution: Dict[str, Optional[str]] = defaultdict(lambda: None)

@app.post("/submit_execution/{session_id}")
async def submit_execution(session_id: str, request: dict):
    """Web UI calls this to send generated code back to Blender."""
    code = request.get("code")
    if code:
        pending_execution[session_id] = code
        logger.info(f"Execution pending for session: {session_id}")
        return {"status": "queued"}
    return {"status": "error", "message": "No code provided"}

@app.get("/get_pending_code/{session_id}")
async def get_pending_code(session_id: str):
    """Blender polls this to see if the UI has sent code to execute."""
    code = pending_execution.get(session_id)
    if code:
        pending_execution[session_id] = None # Clear after retrieval
        return {"code": code}
    return {"code": None}

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
