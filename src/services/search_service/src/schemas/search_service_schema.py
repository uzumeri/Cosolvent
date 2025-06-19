from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AssetReadyForIndexing(BaseModel):
    asset_id: str
    user_id: str
    description: str

class SearchRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    top_k: int = 10

class SearchResult(BaseModel):
    asset_id: str
    score: float
    metadata: dict

class SearchResponse(BaseModel):
    results: List[SearchResult]
