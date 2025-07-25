import json
import re
import os
from typing import List, Optional
from ..tools.base import BaseTool

class FileReader(BaseTool):
    async def execute(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist")
        with open(file_path, "r") as file:
            return file.read()

class FileCreator(BaseTool):
    async def execute(self, file_path: str, content: str) -> str:
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "w") as file:
            file.write(content)
        return f"File {file_path} was created"

class FileEditor(BaseTool):
    def __init__(self, openai_client):
        self.openai_client = openai_client
    
    async def execute(self, file_path: str, edit_instructions: str, 
                     context: str = "", model: str = "gpt-4.1") -> str:
        system_instruction = "You are a precise file editor that modifies text files based on natural language instructions."
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist")
        with open(file_path, "r") as file:
            old_content = file.read()
        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": old_content}
            ],
            max_tokens=32768
        )
        new_content = response.choices[0].message.content
        with open(file_path, "w") as file:
            file.write(new_content)
        return f"File {file_path} was edited"

class RegexApplier(BaseTool):
    async def execute(self, file_path: str, pattern: str, replacement: str,
                     flags: Optional[List[str]] = None, count: int = 0) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist")
        regex_flags = 0
        if flags:
            for flag in flags:
                if hasattr(re, flag.upper()):
                    regex_flags |= getattr(re, flag.upper())
                else:
                    raise ValueError(f"Invalid regex flag: {flag}")
        with open(file_path, "r") as file:
            original_content = file.read()
        new_content = re.sub(
            pattern=pattern,
            repl=replacement,
            string=original_content,
            count=count,
            flags=regex_flags
        )
        with open(file_path, "w") as file:
            file.write(new_content)
        return json.dumps({
            "file_path": file_path,
            "pattern": pattern,
            "replacement": replacement,
            "content_changed": original_content != new_content,
            "original_length": len(original_content),
            "new_length": len(new_content)
        }, indent=3)