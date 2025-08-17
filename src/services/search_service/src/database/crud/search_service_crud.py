from typing import List, Dict, Any, Optional
from src.database.db import index


def upsert_vector(asset_id: str, vector: List[float], metadata: Dict[str, Any]) -> None:
    """Upsert a single vector with metadata to Pinecone."""
    index.upsert(vectors=[(asset_id, vector, metadata)])


def query_vectors(
    vector: List[float],
    filters: Optional[Dict[str, Any]] = None,
    top_k: int = 10
) -> List[Dict[str, Any]]:
    """Query Pinecone for nearest vectors with optional filters."""
    resp = index.query(
        vector=vector,
        filter=filters or {},
        top_k=top_k,
        include_metadata=True
    )
    return resp.matches