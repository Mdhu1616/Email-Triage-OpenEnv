"""
FastAPI server for EmailTriage OpenEnv
Exposes endpoints for /reset, /step, /state, /health
Includes Swagger docs for easy API exploration
"""
from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Optional, Dict, Any
from env.environment import EmailTriageEnv
from env.models import Action

app = FastAPI(title="EmailTriage OpenEnv API", version="1.0")

# In-memory envs by session (for demo; production: use DB or session manager)
envs: Dict[str, EmailTriageEnv] = {}

class ResetRequest(BaseModel):
    task_id: str
    seed: Optional[int] = 42
    session_id: str = "default"

class StepRequest(BaseModel):
    session_id: str = "default"
    action: Dict[str, Any]

class StateRequest(BaseModel):
    session_id: str = "default"

@app.post("/reset")
def reset(req: ResetRequest):
    env = EmailTriageEnv(task_id=req.task_id, seed=req.seed)
    envs[req.session_id] = env
    obs = env.reset(seed=req.seed)
    return {"observation": obs}

@app.post("/step")
def step(req: StepRequest):
    env = envs[req.session_id]
    action = Action(**req.action)
    obs, reward, done, info = env.step(action)
    return {
        "observation": obs,
        "reward": reward,
        "done": done,
        "info": info,
    }

@app.get("/state")
def state(session_id: str = "default"):
    env = envs[session_id]
    return {"state": env.state()}

@app.get("/health")
def health():
    return {"status": "healthy"}
