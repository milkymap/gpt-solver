from openai import AsyncOpenAI
from pandora.definitions import ECHO, READ_FILE, WRITE_FILE, WEB_SEARCH, EXECUTE_BASH

from os import path, listdir, makedirs
import subprocess
import json

class ToolsHandler:
    ECHO = ECHO
    READ_FILE = READ_FILE
    WRITE_FILE = WRITE_FILE
    WEB_SEARCH = WEB_SEARCH
    EXECUTE_BASH = EXECUTE_BASH

    def __init__(self, openai_api_key:str):
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
    
    def get_tool_definitions(self):
        return [
            ToolsHandler.ECHO,
            ToolsHandler.READ_FILE,
            ToolsHandler.WRITE_FILE,
            ToolsHandler.WEB_SEARCH,
            ToolsHandler.EXECUTE_BASH
        ]
    
    async def echo(self, message:str) -> str:
        print(message)
        return f"{message} was displayed to the user"
    
    async def read_file(self, file_path:str) -> str:
        if not path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist")
        with open(file_path, "r") as file:
            return file.read()
    
    async def write_file(self, file_path:str, content:str) -> str:
        makedirs(path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as file:
            file.write(content)
        return f"File {file_path} was created"
    
    async def web_search(self, query:str, model:str="gpt-4o-mini-search-preview", search_context_size:str="low", max_tokens:int=1024) -> str:
        response = await self.openai_client.chat.completions.create(
            model=model,
            web_search_options={
                "search_context_size": search_context_size
            },
            messages=[
                {
                    "role": "user",
                    "content": query
                }
            ],
            max_tokens=max_tokens
        )
        content = response.choices[0].message.content
        return content
    
    async def execute_bash(self, command:str, timeout:int=10) -> str:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return json.dumps({
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }, indent=3)