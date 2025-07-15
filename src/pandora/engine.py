import asyncio 
import json
from enum import Enum
from operator import itemgetter, attrgetter
from typing import List, Tuple, Dict, Any, Optional, AsyncIterable, AsyncGenerator

from pydantic import BaseModel

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionChunk, ChatCompletion, ParsedChatCompletion
from pandora.log import logger 
from pandora.system_config import SystemConfig
from pandora.types import ChatMessage, FinishReason, Role
from pandora.tools import ToolsHandler


class Engine:
    def __init__(self, openai_api_key:str, model:str="gpt-4.1"):
        assert openai_api_key
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        self.model = model 
        self.tools_handler = ToolsHandler(openai_api_key=openai_api_key)
    
    async def handle_messages(self, messages:List[ChatMessage]) -> AsyncIterable[ChatCompletionChunk]:
        response = await self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                ChatMessage(role=Role.SYSTEM, content=SystemConfig.ACTOR_SYSTEM_PROMPT),
                *messages
            ],
            stream=True, 
            max_tokens=4096,
            tool_choice="auto",
            parallel_tool_calls=True,
            tools=self.tools_handler.get_tool_definitions()
        )
        return response
    
    async def handle_response(self, response:AsyncIterable[ChatCompletionChunk]) -> Tuple[str, str, Dict[int, Dict[str, Any]]]:
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
                continue

            tools_hmap[tool_calls[0].index].function.arguments += tool_calls[0].function.arguments
        
        return finish_reason, content, tools_hmap
    
    async def handle_assistant_response(self, stop_reason:str, content:str, tools_hmap:Dict[int, Dict[str, Any]]) -> List[ChatMessage]:
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
                if finish_reason != FinishReason.TOOL_CALLS:
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
    

    async def handle_tool_call(self, tool_call:Dict[str, Any]):
        tool_call_id = tool_call.id
        name = tool_call.function.name
        arguments = tool_call.function.arguments
        try:
            kwargs = json.loads(arguments)
            print(f"kwargs {kwargs}")
            target_function = attrgetter(name)(self.tools_handler)
            result = await target_function(**kwargs)
            print(f"result {result}")
        except Exception as e:
            logger.error(e)
            result = f"Error: {str(e)}"

        return ChatMessage(
            role=Role.TOOL,
            content=result,
            tool_call_id=tool_call_id
        )

if __name__ == "__main__":
    from os import getenv
    from dotenv import load_dotenv
    load_dotenv()
    engine = Engine(openai_api_key=getenv("OPENAI_API_KEY"))
    asyncio.run(engine.loop())