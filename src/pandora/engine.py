import asyncio 
import json
import copy
from operator import attrgetter
from typing import List, Tuple, Dict, Any, Optional, AsyncIterable, Self

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionChunk
from pandora.log import logger 
from pandora.system_config import SystemConfig
from pandora.types import ChatMessage, FinishReason, Role
from pandora.mcp_servers_handler import MCPHandler
from pandora.tools import ToolExecutor, FLAGS
from pandora.definitions import (
    PRINT_MESSAGE, READ_FILE, CREATE_FILE, 
    EDIT_FILE, SEARCH_THROUGH_WEB, GENERATE_PLAN, EXECUTE_BASH, APPLY_REGEX
)

class Engine:
    def __init__(self, mcp_handler: MCPHandler, openai_api_key: str, model: str = "gpt-4.1", 
                 parallel_tool_calls: bool = True, default_print_mode: str = "rich"):
        self.model = model 
        self.openai_api_key = openai_api_key
        self.default_print_mode = default_print_mode
         
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        self.parallel_tool_calls = parallel_tool_calls
        self.mcp_handler = mcp_handler
        
        # Engine state management
        self.internal_state = 0  # 0: interactive, 1: autonomous
        self.engine_state = {"internal_state": self.internal_state}
        
        # Tool executor setup
        self.tool_executor = ToolExecutor(
            openai_client=self.openai_client,
            engine_state=self.engine_state,
            default_print_mode=default_print_mode  # Pass default print mode
        )
        
    async def __aenter__(self) -> Self:
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type is not None:
            logger.error(exc_value)
            logger.exception(traceback)
    
    async def handle_messages(self, messages: List[ChatMessage]) -> AsyncIterable[ChatCompletionChunk]:
        # Create modified print_message tool with CLI default
        modified_print_message = copy.deepcopy(PRINT_MESSAGE)
        modified_print_message["function"]["parameters"]["properties"]["print_mode"]["default"] = self.default_print_mode
        
        tools = [
            modified_print_message,
            READ_FILE, CREATE_FILE, 
            EDIT_FILE, SEARCH_THROUGH_WEB, GENERATE_PLAN, EXECUTE_BASH, APPLY_REGEX
        ]
        for tool in self.mcp_handler.get_tools():
            tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["inputSchema"]
                }
            })

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
    
    async def handle_response(self, response: AsyncIterable[ChatCompletionChunk]) -> Tuple[str, str, Dict[int, Dict[str, Any]]]:
        finish_reason, content, tools_hmap = FinishReason.STOP, "", {}
        async for chunk in response:
            if chunk.choices[0].finish_reason is not None:
                finish_reason = chunk.choices[0].finish_reason
                
            delta_content = chunk.choices[0].delta.content or ""
            print(delta_content, end="", flush=True)  
            content = content + delta_content
            tool_calls = chunk.choices[0].delta.tool_calls
            if tool_calls is None:
                continue
            if len(tool_calls) == 0:
                continue
            if tool_calls[0].index not in tools_hmap:
                tools_hmap[tool_calls[0].index] = tool_calls[0]
                logger.info(f"{tool_calls[0].function.name} will be called")
                continue

            tools_hmap[tool_calls[0].index].function.arguments += tool_calls[0].function.arguments
        
        print("")
        return finish_reason, content, tools_hmap
    
    async def handle_assistant_response(self, stop_reason: str, content: str, tools_hmap: Dict[int, Dict[str, Any]]) -> List[ChatMessage]:
        messages = []
        match stop_reason:
            case FinishReason.STOP:
                messages.append(
                    ChatMessage(
                        role=Role.ASSISTANT,
                        content=content
                    )
                )
            case FinishReason.TOOL_CALLS:
                messages.append(
                    ChatMessage(
                        role=Role.ASSISTANT,
                        tool_calls=[tool_call.model_dump() for tool_call in tools_hmap.values()]
                    )
                )
                async_call = []
                for index, tool_call in tools_hmap.items():
                    async_call.append(self.handle_tool_call(tool_call))
                result = await asyncio.gather(*async_call, return_exceptions=True)
                messages.extend(result)
            case _:
                pass
        return messages
                
    async def loop(self):
        keep_looping = True 
        query = ""
        finish_reason, messages = FinishReason.STOP, []
        while keep_looping:
            try:
                if self.internal_state == 0 or finish_reason != FinishReason.TOOL_CALLS:
                    query = input("Enter a query: ")
                    messages.append(ChatMessage(role=Role.USER, content=query))
                if query in ["EXIT", "exit", "q", "quit"]:
                    keep_looping = False 
                    continue
                response = await self.handle_messages(messages)
                finish_reason, content, tools_hmap = await self.handle_response(response)
                messages_delta = await self.handle_assistant_response(finish_reason, content, tools_hmap)
                messages.extend(messages_delta)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"engine loop error: {e}")
                await asyncio.sleep(1)
    

    async def handle_tool_call(self, tool_call: Dict[str, Any]):
        tool_call_id = tool_call.id
        name = tool_call.function.name
        arguments = tool_call.function.arguments
        try:
            # Update engine state before tool execution
            if self.internal_state == 0 and name != "print_message":
                self.internal_state = 1
                self.engine_state["internal_state"] = 1  # Sync with tool executor
            
            kwargs = json.loads(arguments)
            print("="*50)
            print(name)
            print("="*50)
            print(json.dumps(kwargs, indent=3))
            
            if "mcp__" in name:
                result = await self.mcp_handler.execute_tool(name=name, arguments=kwargs)
            else:
                # Get method from tool executor
                target_function = getattr(self.tool_executor, name)
                result = await target_function(**kwargs)
            
            # Skip printing results for print_message
            if name != "print_message":
                print(result)
                
            # Update engine state after tool execution
            self.internal_state = self.engine_state["internal_state"]
        except Exception as e:
            logger.error(e)
            result = f"Error: {str(e)}"

        return ChatMessage(
            role=Role.TOOL,
            content=result,
            tool_call_id=tool_call_id
        )
