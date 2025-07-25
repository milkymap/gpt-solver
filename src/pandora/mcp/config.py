from pydantic import BaseModel
from typing import List, Dict, Optional

class MCPConfig(BaseModel):
    command: str 
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None

class MCPServersConfig(BaseModel):
    mcpServers: Dict[str, MCPConfig]