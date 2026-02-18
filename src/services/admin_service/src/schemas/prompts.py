from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SystemPrompt(BaseModel):
    id: str
    prompt: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class SystemPromptUpdate(BaseModel):
    prompt: str
