from enum import Enum
from pydantic import BaseModel
from typing import Optional, Dict, Any, List 

class FinishReason(str, Enum):
    STOP = "stop"
    TOOL_CALLS = "tool_calls"


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

class ChatMessage(BaseModel):
    role:Role
    content:Optional[str] = None
    tool_call_id:Optional[str] = None
    tool_calls:Optional[List[Dict[str, Any]]] = None