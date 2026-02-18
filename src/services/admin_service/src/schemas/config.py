from pydantic import BaseModel
from typing import Dict, Any, Optional

class SystemConfig(BaseModel):
    clients: Dict[str, Any]
    services: Dict[str, Any]

class ConfigUpdate(BaseModel):
    clients: Optional[Dict[str, Any]] = None
    services: Optional[Dict[str, Any]] = None
