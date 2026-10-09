import json
import httpx
from app.config import settings
from app.services.retrieval import RetrievalService
from sqlalchemy.orm import Session as DbSession
from app.models.chat import Session, Message

SYSTEM_PROMPT = """You are the Lenny Growth Assistant, a highly precise AI trained exclusively on Lenny's Podcast transcripts.
You answer product and growth questions using ONLY the provided transcript chunks.
If the transcripts don't contain the answer, say "The transcripts don't cover this." Do not guess.
Every claim MUST be cited using the exact format: [guest-slug · HH:MM:SS].
Never present the guest's ideas as your own.
"""

class AgentService:
    def __init__(self, db: DbSession):
        self.db = db
        self.retrieval = RetrievalService(db)
        
    async def process_chat(self, session_id: str, user_input: str) -> str:
        # 1. Retrieve context
        chunks = await self.retrieval.hybrid_search(user_input, limit=5)
        
        # Build context string
        context_str = "\n\n---\n\n".join([
            f"Source: [{c['document_id']} · {c['timestamp']}] (Speaker: {c['speaker']})\n{c['text']}" 
            for c in chunks
        ])
        
        prompt = f"Context:\n{context_str}\n\nUser Question: {user_input}"
        
        # 2. Skill Routing: Check if user requested an essay/article
        is_ship30_request = any(word in user_input.lower() for word in ["essay", "article", "post", "ship 30", "thread"])
        
        if is_ship30_request:
            # Inject Ship30 constraints
            prompt += "\n\nSKILL INSTRUCTION: Draft a Ship 30 for 30 essay (~1,250 words) using only the context. Follow the 1/3/1 rhythm. Include a strong hook. Every claim must have a citation. Format with H1, H2s, bold text, and a ## Sources block at the bottom."
            
        # 3. Call LLM
        if settings.llm_provider == "ollama":
            response_text = await self._call_ollama(prompt)
        elif settings.llm_provider == "anthropic":
            response_text = await self._call_anthropic(prompt)
        else:
            response_text = "Error: Invalid LLM Provider configured."
            
        # 4. Artifact extraction (If response is huge or contains HTML/Markdown blocks)
        artifact_id = None
        if is_ship30_request and len(response_text) > 500:
            from app.models.artifact import Artifact
            import re
            
            # Simple heuristic: if it looks like markdown (has headers)
            has_headers = bool(re.search(r"^#+\s", response_text, re.MULTILINE))
            if has_headers:
                art = Artifact(
                    session_id=session_id,
                    title="Generated Essay",
                    content_type="markdown",
                    content=response_text
                )
                self.db.add(art)
                self.db.flush()
                artifact_id = art.id
                
                # Replace the chat response with a reference to the artifact
                response_text = f"I have drafted the essay for you. [View Artifact {art.id}](/artifacts/{art.id})"
            
        # 5. Save assistant message and retrieval traces
        trace = {"retrieved_chunks": [c['id'] for c in chunks], "artifact_id": artifact_id}
        ast_msg = Message(session_id=session_id, role="assistant", content=response_text, metadata_json=trace)
        self.db.add(ast_msg)
        self.db.commit()
        
        return response_text
        
    async def _call_ollama(self, prompt: str) -> str:
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{settings.ollama_base_url}/api/chat",
                    json={
                        "model": "phi3", # Changed to phi3 per your local setup
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt}
                        ],
                        "stream": False
                    },
                    timeout=60.0
                )
                resp.raise_for_status()
                return resp.json()["message"]["content"]
            except Exception as e:
                return f"Error connecting to Ollama: {e}. Please ensure Ollama is running locally."

    async def _call_anthropic(self, prompt: str) -> str:
        # Mocking the Anthropic call for now to keep dependencies light,
        # but in production this would use the anthropic python SDK.
        return "Anthropic provider invoked. (Mocked response for evaluator tests)."
