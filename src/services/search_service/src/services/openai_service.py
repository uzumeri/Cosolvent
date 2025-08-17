# app/services/openai_service.py
from openai import OpenAI
from typing import List

from src.core.config import settings

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_model = settings.OPENAI_EMBEDDING_MODEL
        self.embedding_dimension = settings.OPENAI_EMBEDDING_DIMENSION

    def get_embedding(self, text: str) -> List[float]:
        """
        Generates an embedding for a given text string.
        """
        try:
            # OpenAI API expects a list of strings, even for a single string
            response = self.client.embeddings.create(
                input=[text],
                model=self.embedding_model
            )
            # Ensure the embedding dimension matches the configured one
            if len(response.data[0].embedding) != self.embedding_dimension:
                raise ValueError(
                    f"Embedding dimension mismatch: Expected {self.embedding_dimension}, "
                    f"got {len(response.data[0].embedding)} from model {self.embedding_model}"
                )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding from OpenAI: {e}")
            raise

# Initialize the OpenAI service
openai_service = OpenAIService()