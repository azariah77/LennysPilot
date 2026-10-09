from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import engine, get_db
from app.config import settings

app = FastAPI(
    title="Lenny Growth Assistant API",
    description="API for the Lenny Growth Assistant.",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_index():
    return FileResponse("static/index.html")

@app.get("/health")
def health_check():
    """Liveness probe to check if the API is running."""
    return {"status": "ok", "environment": settings.environment}

@app.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    """Readiness probe to check DB connection and model configurations."""
    status = {"status": "ready", "checks": {}}
    
    # Check Database
    try:
        db.execute(text("SELECT 1"))
        status["checks"]["database"] = "ok"
    except Exception as e:
        status["checks"]["database"] = f"error: {str(e)}"
        status["status"] = "not_ready"
        
    # Check LLM Config
    if settings.llm_provider == "anthropic" and not settings.anthropic_api_key:
        status["checks"]["llm"] = "error: missing anthropic API key"
        status["status"] = "not_ready"
    else:
        status["checks"]["llm"] = f"configured for {settings.llm_provider}"
        
    if status["status"] != "ready":
        raise HTTPException(status_code=503, detail=status)
        
    return status

from pydantic import BaseModel
from app.models.chat import Session as DBSession, Message as DBMessage
from app.services.agent import AgentService

class ChatRequest(BaseModel):
    message: str

@app.post("/sessions")
def create_session(db: Session = Depends(get_db)):
    """Creates a new chat session."""
    session = DBSession()
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"session_id": session.id}

@app.post("/sessions/{session_id}/chat")
async def chat(session_id: str, req: ChatRequest, db: Session = Depends(get_db)):
    """Processes a user message through the agent."""
    # Validate session
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Save user message
    user_msg = DBMessage(session_id=session_id, role="user", content=req.message)
    db.add(user_msg)
    db.commit()
    
    agent = AgentService(db)
    response = await agent.process_chat(session_id, req.message)
    
    return {"response": response}

from fastapi.responses import HTMLResponse, Response
from app.models.artifact import Artifact as DBArtifact

@app.get("/artifacts/{artifact_id}")
def get_artifact(artifact_id: str, db: Session = Depends(get_db)):
    """Retrieves an artifact with strict security sandboxing."""
    artifact = db.query(DBArtifact).filter(DBArtifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
        
    if artifact.content_type == "html":
        # DEFENSE IN DEPTH: Strict CSP + Sandbox
        # 'default-src none': blocks all network requests (images, scripts, frames)
        # 'style-src unsafe-inline': allows inline CSS to render the artifact
        # 'sandbox': enforces iframe restriction, no allow-scripts, no allow-same-origin
        headers = {
            "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; sandbox;",
            "X-Content-Type-Options": "nosniff"
        }
        return HTMLResponse(content=artifact.content, headers=headers)
    
    # Return markdown safely
    headers = {"X-Content-Type-Options": "nosniff"}
    return Response(content=artifact.content, media_type="text/markdown", headers=headers)
