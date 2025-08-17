# database/models/template_model.py
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID, uuid4

class TemplateModel(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    content: str
    is_active: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
