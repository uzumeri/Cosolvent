from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class MCPServer(BaseModel):
    name: str
    url: str
    description: Optional[str] = None
    enabled: bool = True
    capabilities: List[str] = []

class MCPServerList(BaseModel):
    servers: List[MCPServer]
