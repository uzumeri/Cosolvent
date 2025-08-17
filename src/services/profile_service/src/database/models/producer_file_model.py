# profile_model.py
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class ProducerFileModel(BaseModel):
    id: str = Field(..., alias="_id")
    profile_id: str
    url: str
    file_type: str
    certification: Optional[str] = None
    description: Optional[str] = None  # AI-generated metadata description
    priority: Optional[int] = 0
    privacy: Optional[str] = "private"
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

