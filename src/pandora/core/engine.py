import asyncio
import json
from typing import List, Dict, Any, Optional, AsyncIterable
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionChunk
from .state import EngineState
from .tool_executor import ToolExecutor
from pandora.mcp.handler import MCPHandler
from pandora.definitions.tool_definitions import get_core_tools
from pandora.types import ChatMessage, FinishReason, Role
from pandora.config import SystemConfig
from pandora.log import logger

class Engine:
    def __init__(self, mcp_handler: MCPHandler, openai_api_key: str, model: str = "gpt-4.1", 
                 parallel_tool_calls: bool = True, default_print_mode: str = "rich"):
        self.model = model 
        self.openai_api_key = openai_api_key
        self.default_print_mode = default_print_mode
        self.parallel_tool_calls = parallel_tool_calls
        self.mcp_handler = mcp_handler
        
        # Engine state management
        self.engine_state = EngineState()
        
        # Tool executor setup
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        self.tool_executor = ToolExecutor(
            openai_client=self.openai_client,
            engine_state=self.engine_state,
            default_print_mode=default_print_mode
        )
    
    async def __aenter__(self) -> 'Engine':
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type is not None:
            logger.error(f"Engine error: {exc_value}")
            logger.exception(traceback)

    async def _get_tools(self) -> List[Dict[str, Any]]:
        """Get all available tools including MCP tools."""
        tools = get_core_tools(self.default_print_mode)
        mcp_tools = self.mcp_handler.get_tools()
        
        if not mcp_tools:
            logger.warning("No MCP tools found. Check server configurations.")
        else:
            logger.info(f"Found {len(mcp_tools)} MCP tools")
            
        for tool in mcp_tools:
            tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["inputSchema"]
                }
            })
        return tools

    async def handle_messages(self, messages: List[ChatMessage]) -> AsyncIterable[ChatCompletionChunk]:
        tools = await self._get_tools()
        response = await self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                ChatMessage(role=Role.SYSTEM, content=SystemConfig.ACTOR_SYSTEM_PROMPT),
                *messages
            ],
            stream=True, 
            max_tokens=8192,
            tool_choice="required",
            tools=tools,
            parallel_tool_calls=self.parallel_tool_calls,
        )
        return response
    
    async def handle_response(self, response: AsyncIterable[ChatCompletionChunk]) -> tuple:
        finish_reason, content, tools_hmap = FinishReason.STOP, "", {}
        async for chunk in response:
            if chunk.choices[0].finish_reason is not None:
                finish_reason = chunk.choices[0].finish_reason
            delta_content = chunk.choices[0].delta.content or ""
            print(delta_content, end="", flush=True)  
            content = content + delta_content
            tool_calls = chunk.choices[0].delta.tool_calls
            if tool_calls:
                await self._process_tool_calls(tool_calls, tools_hmap)
        print("")
        return finish_reason, content, tools_hmap
    
    async def _process_tool_calls(self, tool_calls, tools_hmap):
        if not tool_calls:
            return
        if tool_calls[0].index not in tools_hmap:
            tools_hmap[tool_calls[0].index] = tool_calls[0]
            logger.info(f"Tool will be called: {tool_calls[0].function.name}")
            return
        tools_hmap[tool_calls[0].index].function.arguments += tool_calls[0].function.arguments
    
    async def handle_assistant_response(self, stop_reason: str, content: str, 
                                      tools_hmap: Dict[int, Dict[str, Any]]) -> List[ChatMessage]:
        messages = []
        match stop_reason:
            case FinishReason.STOP:
                messages.append(ChatMessage(
                    role=Role.ASSISTANT,
                    content=content
                ))
            case FinishReason.TOOL_CALLS:
                messages.append(ChatMessage(
                    role=Role.ASSISTANT,
                    tool_calls=[tool_call.model_dump() for tool_call in tools_hmap.values()]
                ))
                results = await self._execute_tools(tools_hmap)
                messages.extend(results)
        return messages
                
    async def _execute_tools(self, tools_hmap: Dict[int, Dict[str, Any]]) -> List[ChatMessage]:
        async_calls = []
        for _, tool_call in tools_hmap.items():
            async_calls.append(self._execute_single_tool(tool_call))
        return await asyncio.gather(*async_calls, return_exceptions=True)

    async def _execute_single_tool(self, tool_call: Dict[str, Any]) -> ChatMessage:
        """Execute a single tool call."""
        tool_call_id = tool_call.id
        name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        
        try:
            # Update engine state before tool execution
            if self.engine_state.internal_state == 0 and name != "print_message":
                self.engine_state.internal_state = 1
            
            logger.info(f"Executing tool: {name}")
            
            # Check if this is an MCP tool
            if name.startswith("mcp__"):
                result = await self.mcp_handler.execute_tool(name, arguments)
            else:
                result = await self.tool_executor.execute_tool(name, arguments)
            
            # Skip printing results for print_message
            if name != "print_message":
                print(result)
                
            return ChatMessage(
                role=Role.TOOL,
                content=result,
                tool_call_id=tool_call_id
            )
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return ChatMessage(
                role=Role.TOOL,
                content=f"Error: {str(e)}",
                tool_call_id=tool_call_id
            )

    async def loop(self):
        keep_looping = True 
        messages = []

        # Debug: Log registered tools
        tools = await self._get_tools()
        logger.info(f"Registered tools: {[t['function']['name'] for t in tools if t['type'] == 'function']}")
   
        while keep_looping:
            try:
                if self.engine_state.internal_state == 0 or not messages:
                    query = input("Enter a query: ")
                    if query.lower() in ["exit", "quit", "q"]:
                        break
                    messages.append(ChatMessage(role=Role.USER, content=query))
                response = await self.handle_messages(messages)
                finish_reason, content, tools_hmap = await self.handle_response(response)
                new_messages = await self.handle_assistant_response(finish_reason, content, tools_hmap)
                messages.extend(new_messages)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Engine loop error: {e}")
                await asyncio.sleep(1)