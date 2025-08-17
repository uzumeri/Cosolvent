from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from .profile_model import PyObjectId
from .producer_file_model import ProducerFileModel

class ApplicationModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
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
    export_experience: str
    primary_crops: List[str]
    certifications: Optional[List[str]] = []
    files: Optional[List[ProducerFileModel]] = []
    status: str # e.g., 'pending_review', 'rejected'
    rejection_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
