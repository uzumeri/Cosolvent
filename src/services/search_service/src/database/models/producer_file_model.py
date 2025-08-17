# profile_model.py
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class ProducerFileModel(BaseModel):
    id: str
    profile_id: str
    url: str
    file_type: str
    certification: Optional[str] = None
    description: Optional[str] = None  
    priority: Optional[int] = 0
    privacy: Optional[str] = "private"

