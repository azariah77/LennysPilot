import httpx
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.provider = settings.llm_provider
        self.ollama_base_url = settings.ollama_base_url.rstrip("/")
        # We will assume nomic-embed-text for Ollama local (dim=768)
        self.ollama_model = "nomic-embed-text" 
    
    async def get_embedding(self, text: str) -> list[float]:
        """Gets embedding using the configured provider."""
        if self.provider == "ollama":
            return await self._get_ollama_embedding(text)
        elif self.provider == "anthropic":
            # Anthropic doesn't have an embedding model currently, 
            # so we'd fallback to a cloud OpenAI or Voyage.
            # For this take-home, local Ollama is the focus.
            # We'll use Ollama as a fallback for embeddings even if Anthropic is the LLM.
            logger.warning("Anthropic provider selected but Anthropic lacks embeddings. Falling back to local Ollama for embeddings.")
            return await self._get_ollama_embedding(text)
        else:
            raise ValueError(f"Unknown LLM Provider: {self.provider}")

    async def _get_ollama_embedding(self, text: str) -> list[float]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.ollama_base_url}/api/embeddings",
                    json={"model": self.ollama_model, "prompt": text},
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("embedding", [])
            except Exception as e:
                logger.error(f"Failed to get embedding from Ollama: {e}")
                # Return empty list or raise to signal failure gracefully
                raise RuntimeError(f"Embedding failure: {e}")
