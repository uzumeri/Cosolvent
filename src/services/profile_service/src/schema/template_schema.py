# schema/template_schema.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class TemplateCreate(BaseModel):
    name: str
    content: str

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None

class TemplateResponse(BaseModel):
    id: UUID 
    name: str
    content: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        allow_population_by_field_name = True
