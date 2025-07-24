import json
import re
import subprocess
from os import path, makedirs
from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI
from rich import print as rprint
from rich.panel import Panel
from rich.text import Text

FLAGS = ["IGNORECASE", "MULTILINE", "DOTALL", "VERBOSE", "ASCII", "LOCALE"]

class ToolExecutor:
    def __init__(self, openai_client: AsyncOpenAI, engine_state: Dict[str, Any], 
                 default_print_mode: str = "rich"):
        self.openai_client = openai_client
        self.engine_state = engine_state
        self.default_print_mode = default_print_mode

    async def print_message(self, message: str, message_type: str, 
                           print_mode: Optional[str] = None) -> str:
        # Use default print mode if not specified
        if print_mode is None:
            print_mode = self.default_print_mode
            
        match message_type:
            case "reply" | "ask" | "confirm":
                self.engine_state["internal_state"] = 0
            case "notify" | "think" | "update" | "analyze":
                self.engine_state["internal_state"] = 1
            case _:
                raise ValueError(f"Invalid message type: {message_type}")
        
        # Rich formatting implementation
        if print_mode == "rich":
            type_colors = {
                "think": "bold blue",
                "ask": "bold yellow",
                "confirm": "bold magenta",
                "analyze": "bold cyan",
                "notify": "bold green",
                "update": "bold white",
                "reply": "bold"
            }
            
            color = type_colors.get(message_type, "bold")
            title = f"{message_type.upper()}"
            
            rprint(Panel(
                Text(message, style=color),
                title=title,
                title_align="left",
                border_style=color,
                padding=(1, 2)
            ))
        else:
            # Default JSON output
            print(message)
        
        return json.dumps({
            "message": message,
            "message_type": message_type,
            "agent_loop_state": "interactive" if self.engine_state["internal_state"] == 0 else "autonomous"
        }, indent=3)
    
    
    async def read_file(self, file_path: str) -> str:
        if not path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist")
        with open(file_path, "r") as file:
            content = file.read()
        return content
    
    async def create_file(self, file_path: str, content: str) -> str:
        dir_path = path.dirname(file_path)
        if dir_path:
            makedirs(dir_path, exist_ok=True)
        with open(file_path, "w") as file:
            file.write(content)
        return f"File {file_path} was created"
    
    async def edit_file(self, file_path: str, edit_instructions: str, context: str = "", model: str = "gpt-4.1") -> str:
        system_instruction = """
        You are a precise file editor that modifies text files based on natural language instructions while preserving structure and context.

        TASK:
        Edit the file content provided by the user according to these instructions: {edit_instructions}

        CONTEXT:
        {context}

        RULES:
        1. Return ONLY the complete modified file content - no explanations, comments, or additional text
        2. Preserve the original file structure, formatting, and style unless explicitly asked to change it
        3. Make only the changes specified in the instructions - do not add unnecessary modifications
        4. Maintain consistency with the existing content patterns and conventions
        5. If the instructions are unclear or would break the file, make minimal conservative changes
        6. Preserve all content that should remain unchanged
        7. Ensure the output is valid and well-formed for the file type

        IMPORTANT:
        - Your entire response will be written directly to the file
        - Do not include markdown code blocks, explanations, or any wrapper text
        - The first character of your response should be the first character of the edited file
        - The last character of your response should be the last character of the edited file

        Apply the edit instructions to the file content that follows.
        """
        if not path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist")
        with open(file_path, "r") as file:
            old_content = file.read()
        
        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_instruction.format(
                        edit_instructions=edit_instructions,
                        context=context
                    )
                }, 
                {
                    "role": "user",
                    "content": old_content
                }
            ],
            max_tokens=32768
        )
        new_content = response.choices[0].message.content
        with open(file_path, "w") as file:
            file.write(new_content)
        return f"File {file_path} was edited, you can now read the file to see the changes"
    
    async def search_through_web(self, query: str, model: str = "gpt-4o-mini-search-preview", 
                                search_context_size: str = "low", max_tokens: int = 1024) -> str:
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
    
    async def execute_bash(self, command: str, timeout: int = 10) -> str:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return json.dumps({
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }, indent=3)
    
    async def generate_plan(self, task: str, reasoning_effort: str, model: str) -> str:
        system_instruction = """
        You are an expert task planner and project manager with deep expertise in software development, automation, and complex problem-solving.

        Your role is to analyze tasks and create comprehensive, actionable execution plans that can be followed by an agentic AI system.

        PLANNING PRINCIPLES:
        - Break down complex tasks into logical, sequential steps
        - Each step should be atomic and clearly defined
        - Consider dependencies between steps
        - Account for potential failure points and error handling
        - Include verification and validation steps
        - Think about resource requirements and constraints

        AVAILABLE TOOLS FOR EXECUTION:
        - read_file: Read file contents
        - create_file: Create/overwrite files
        - edit_file: Modify existing files (use llm to edit/change the file)
        - apply_regex: Apply regex to files (fast editing)
        - search_through_web: Search the web for information
        - execute_bash: Run shell commands
        - generate_plan: Create a plan for a given task
        - manage_tasks: Manage tasks (create, update, delete, list)

        PLAN OUTPUT FORMAT:
        - generate a set of steps to complete the task
        - each step must be described by:
        - title: a short title for the step
        - description: a detailed description of the step
        - priority: the priority of the step (high, medium, low)
        """

        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_instruction
                },
                {
                    "role": "user",
                    "content": f"Task : {task}, please generate a good plan for this task"
                }
            ],
            max_tokens=100_000
        )
        return response.choices[0].message.content
    
    async def apply_regex(
        self,
        file_path: str,
        pattern: str,
        replacement: str,
        flags: Optional[List[str]] = None,
        count: int = 0,
    ) -> str:
        """Apply regex substitution to a file"""
        
        if not path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist")
        
        # Convert string flags to regex flags
        regex_flags = 0
        if flags:
            for flag in flags:
                if flag.upper() in FLAGS:
                    regex_flags |= getattr(re, flag.upper())
                else:
                    raise ValueError(f"Invalid regex flag: {flag}")
        
        # Read file content
        with open(file_path, "r") as file:
            original_content = file.read()
        
        try:
            # Apply regex substitution
            new_content = re.sub(
                pattern=pattern,
                repl=replacement,
                string=original_content,
                count=count,
                flags=regex_flags
            )
            
            # Write modified content back to file
            with open(file_path, "w") as file:
                file.write(new_content)
            
            return json.dumps({
                "file_path": file_path,
                "pattern": pattern,
                "replacement": replacement,
                "content_changed": original_content != new_content,
                "original_length": len(original_content),
                "new_length": len(new_content),
                "new_content": new_content
            }, indent=3)
            
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
