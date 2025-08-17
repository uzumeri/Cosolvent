from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from pydantic import EmailStr
from typing import Dict, Any

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

class CompanyProfile(BaseModel):
    company_name: str
    primary_contact: str
    head_office: str
    region: str
    founded_year: int
    employees: Optional[int]
    description: str
    type_of_operation: str
    products: List[Dict[str, Any]]
    certifications: List[str]
    export_markets: List[str]
    key_people: List[str]
    awards: List[str]
    social_media: Dict[str, str]

class IndividualProfile(BaseModel):
    name: str
    farm_name: str
    contact: str
    email: EmailStr
    phone: str
    region: str
    years_in_operation: int
    languages: List[str]
    farm_description: str
    products_offered: List[Dict[str, Any]]
    certifications: List[str]
    export_experience: Optional[str]
    awards: List[str]
    social_media: Dict[str, str]
