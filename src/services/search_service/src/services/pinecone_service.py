# app/services/pinecone_service.py
from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any, Optional
import time

from src.core.config import settings

class PineconeService:
    _instance: Optional["PineconeService"] = None
    _index: Optional[Pinecone.Index] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PineconeService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def _ensure_initialized(self):
        if self._initialized:
            return
        if not settings.PINECONE_API_KEY:
            raise RuntimeError("PINECONE_API_KEY is not set. Set it in the environment to use Pinecone features.")
        self.pinecone = Pinecone(api_key=settings.PINECONE_API_KEY, environment=settings.PINECONE_ENVIRONMENT)
        self.index_name = settings.PINECONE_INDEX_NAME
        self.dimension = settings.EMBEDDING_DIMENSION
        self.metric = "cosine"
        self._connect_to_index()
        self._initialized = True
        return

    def _connect_to_index(self):
        """Connects to the Pinecone index, creating it if it doesn't exist."""
        existing_indexes = self.pinecone.list_indexes()
        if self.index_name in existing_indexes:
            print(f"Pinecone index '{self.index_name}' already exists. Skipping creation.")
        else:
            print(f"Creating Pinecone index '{self.index_name}'...")
            try:
                self.pinecone.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric=self.metric,
                    spec=ServerlessSpec(cloud="aws", region=settings.PINECONE_ENVIRONMENT)
                )
                # Wait for the index to be initialized
                while not self.pinecone.describe_index(self.index_name).status['ready']:
                    time.sleep(1)
                print(f"Pinecone index '{self.index_name}' created and ready.")
            except Exception as e:
                if hasattr(e, 'status') and getattr(e, 'status', None) == 409:
                    print(f"Index '{self.index_name}' already exists (409). Continuing.")
                elif "ALREADY_EXISTS" in str(e):
                    print(f"Index '{self.index_name}' already exists (ALREADY_EXISTS). Continuing.")
                else:
                    raise
        self._index = self.pinecone.Index(self.index_name)
        print(f"Connected to Pinecone index: {self._index.describe_index_stats()}")

    def upsert_vectors(self, vectors: List[Dict[str, Any]]):
        """
        Upserts vectors to the Pinecone index.
        Vectors should be a list of dictionaries with 'id', 'values', and 'metadata'.
        Example: [{"id": "doc1", "values": [0.1, 0.2, ...], "metadata": {"key": "value"}}]
        """
        self._ensure_initialized()
        if not self._index:
            raise ConnectionError("Pinecone index not initialized.")
        try:
            self._index.upsert(vectors=vectors)
            return True
        except Exception as e:
            print(f"Error upserting vectors to Pinecone: {e}")
            raise

    def query_vectors(self, vector: List[float], top_k: int, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Queries the Pinecone index with a given vector.
        Returns top_k matches with their metadata.
        Filters allow narrowing down the search results by metadata.
        """
        self._ensure_initialized()
        if not self._index:
            raise ConnectionError("Pinecone index not initialized.")
        try:
            query_response = self._index.query(vector=vector, top_k=top_k, include_metadata=True, filter=filters)
            return query_response.matches or []
        except Exception as e:
            print(f"Error querying Pinecone: {e}")
            raise
    def delete_all_vectors(self) -> bool:
        """
        Deletes all vectors from the Pinecone index.
        """
        self._ensure_initialized()
        if not self._index:
            raise ConnectionError("Pinecone index not initialized.")
        try:
            self._index.delete(delete_all=True)
            print(f"All vectors deleted from index '{self.index_name}'.")
            return True
        except Exception as e:
            print(f"Error deleting vectors from Pinecone: {e}")
            raise

# Initialize the Pinecone service on application startup
pinecone_service = PineconeService()