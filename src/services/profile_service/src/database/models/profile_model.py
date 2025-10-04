from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from .producer_file_model import ProducerFileModel


class ProducerModel(BaseModel):
    id: str = Field(..., alias="_id")
    farm_name: str
    contact_name: str
    email: EmailStr
    phone: str
    address: str
    country: str
    region: str
    farm_size: float
    annual_production: float
    farm_description: str
    primary_crops: List[str]
    certifications: Optional[List[str]] = []
    export_experience: str
    status: str
    files: Optional[List[ProducerFileModel]] = []
    ai_profile: Optional[str] = None
    ai_profile_draft: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        allow_population_by_field_name = True