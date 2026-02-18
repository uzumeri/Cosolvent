from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class ParticipantField(BaseModel):
    name: str
    type: str # string, number, boolean, array, object
    description: str
    required: bool = False

class MarketDefinition(BaseModel):
    name: str
    description: str
    participant_schema: List[ParticipantField]
    matching_logic_prompt_id: Optional[str] = None
    extraction_logic_prompt_id: Optional[str] = None
