from typing import List
import httpx
from src.core.config import settings


class EmbeddingService:
    def __init__(self):
        self.dimension = settings.EMBEDDING_DIMENSION
        self.orchestrator_url = "http://llm_orchestration_service:8000"

    def get_embedding(self, text: str) -> List[float]:
        try:
            payload = {"text": text, "service_name": "embeddings"}
            with httpx.Client(timeout=30) as client:
                r = client.post(f"{self.orchestrator_url}/llm/embeddings", json=payload)
                r.raise_for_status()
                data = r.json()
                embedding = data.get("result")
            if len(embedding) != self.dimension:
                raise ValueError(
                    f"Embedding dimension mismatch: expected {self.dimension}, got {len(embedding)}"
                )
            return embedding
        except Exception as e:
            print(f"Error getting embedding from OpenRouter via orchestrator: {e}")
            raise


embedding_service = EmbeddingService()
