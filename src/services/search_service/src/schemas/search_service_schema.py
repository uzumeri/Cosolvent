from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class SearchRequest(BaseModel):
    query: str
    country: Optional[str] = None
    categories: Optional[List[str]] = None
    top_k: Optional[int] = 100

class SearchResponseItem(BaseModel):
    user_id: str
    score: float
    metadata: Optional[Dict[str, Any]] = None

class SearchResponse(BaseModel):
    results: List[SearchResponseItem]
