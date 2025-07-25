import json
from typing import Dict, Any, Optional
from rich import print as rprint
from rich.panel import Panel
from rich.text import Text
from .state import EngineState
from pandora.tools.messaging import MessageFormatter
from pandora.tools.base import BaseTool
from pandora.log import logger

class ToolExecutor:
    def __init__(self, openai_client, engine_state: EngineState, default_print_mode: str = "rich"):
        self.openai_client = openai_client
        self.engine_state = engine_state
        self.default_print_mode = default_print_mode
        self.message_formatter = MessageFormatter(default_print_mode)
        self._registered_tools: Dict[str, BaseTool] = {}

    def register_tool(self, tool: BaseTool):
        self._registered_tools[tool.__class__.__name__] = tool

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        try:
            if name == "print_message":
                return await self.print_message(**arguments)
            
            tool = self._registered_tools.get(name)
            if tool is None:
                raise ValueError(f"Tool {name} not registered")
                
            return await tool.execute(**arguments)
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            raise

    async def print_message(self, message: str, message_type: str, 
                          print_mode: Optional[str] = None) -> str:
        print_mode = print_mode or self.default_print_mode
        self.engine_state.update_from_message_type(message_type)
        return self.message_formatter.format_message(
            message, 
            message_type, 
            self.engine_state.internal_state
        )