from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ProducerSimilarity(BaseModel):
    """
    Represents a search result with only the producer_id and similarity score.
    Ordered by score (most similar on top).
    """
    producer_id: str = Field(alias="id") # Map user_id from metadata to producer_id
    score: float

class SearchResponse(BaseModel):
    success: bool
    message: str
    error: Optional[str] = None
    results: List[ProducerSimilarity] = Field(default_factory=list)

class QueryRequest(BaseModel):
    query: str
    # Optional filters for search
    filter_region: Optional[str] = None
    filter_certification: Optional[str] = None
    filter_primary_crop: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=100) # Number of results to return

class IndexRequest(BaseModel):
    profile_id: str
    ai_profile: str
    region:str
    certifications: List[str] = Field(default_factory=list)
    primary_crops: List[str] = Field(default_factory=list)
