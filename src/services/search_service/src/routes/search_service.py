import logging
from fastapi import APIRouter, HTTPException
import openai
from src.core.config import settings
from src.core.vector_store import index
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)
router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    country: Optional[str] = None
    categories: Optional[List[str]] = None
    top_k: Optional[int] = 10

class SearchResponseItem(BaseModel):
    user_id: str
    score: float
    metadata: Optional[Dict[str, Any]] = None

class SearchResponse(BaseModel):
    results: List[SearchResponseItem]

@router.post("/search", response_model=SearchResponse)
async def search_profiles(req: SearchRequest):
    top_k = req.top_k or 10
    if top_k < 1 or top_k > 1000:
        raise HTTPException(status_code=400, detail="top_k must be between 1 and 1000")

    try:
        resp = openai.embeddings.create(model=settings.embedding_model, input=[req.query])
        query_emb = resp.data[0].embedding

    except Exception as e:
        logger.error(f"Embedding error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate embedding")

    filter_dict = {}
    if req.country:
        filter_dict["country"] = {"$eq": req.country}
    # Apply categories filter only for non-empty category strings
    valid_categories = [c for c in (req.categories or []) if c and c.strip()]
    if valid_categories:
        # Use $in to match any of the requested categories
        filter_dict["categories"] = {"$in": valid_categories}

    try:
        query_kwargs = {
            "vector": query_emb,
            "top_k": top_k,
            "include_metadata": True
        }
        if filter_dict:
            query_kwargs["filter"] = filter_dict
        result = index.query(**query_kwargs)
        print(result)
    except Exception as e:
        logger.error(f"Pinecone query failed: {e}")
        raise HTTPException(status_code=500, detail="Search query failed")

    items = []
    profiles = []
    for match in result.matches:
        items.append(SearchResponseItem(
            user_id=match.id,
            score=match.score,
            metadata=match.metadata
        ))
    return SearchResponse(results=items)