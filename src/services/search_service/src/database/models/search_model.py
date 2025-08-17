from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ProducerProfile(BaseModel):
    """
    Represents the data structure for a producer's profile,
    which will be indexed.
    """
    user_id: str
    name: str
    description: str
    region: str
    certifications: List[str] = Field(default_factory=list)
    primary_crops: List[str] = Field(default_factory=list)
    # Add other relevant fields that might contribute to the search
    # e.g., product_list: List[str], farming_practices: str

class AIProfile(BaseModel):
    """
    Represents the data structure for an AI-generated profile/summary,
    which will also be indexed.
    """
    user_id: str
    summary_text: str
    # Add other relevant AI-generated insights
    # e.g., key_strengths: List[str]

class IndexResponse(BaseModel):
    success: bool
    message: str
    error: Optional[str] = None
    indexed_id: Optional[str] = None

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