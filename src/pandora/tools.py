from openai import AsyncOpenAI
from google import genai
from pandora.definitions import ECHO, READ_FILE, WRITE_FILE, WEB_SEARCH, EXECUTE_BASH, BUILD_PLAN, GENERATE_CODE

from os import path, listdir, makedirs
import subprocess
import json
import re 

class ToolsHandler:
    ECHO = ECHO
    READ_FILE = READ_FILE
    WRITE_FILE = WRITE_FILE
    WEB_SEARCH = WEB_SEARCH
    EXECUTE_BASH = EXECUTE_BASH
    BUILD_PLAN = BUILD_PLAN
    GENERATE_CODE = GENERATE_CODE

    def __init__(self, openai_api_key:str, gemini_api_key:str):
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        self.gemini_client = genai.Client(api_key=gemini_api_key)
    
    def get_tool_definitions(self):
        return [
            ToolsHandler.ECHO,
            ToolsHandler.READ_FILE,
            ToolsHandler.WRITE_FILE,
            ToolsHandler.WEB_SEARCH,
            ToolsHandler.EXECUTE_BASH,
            ToolsHandler.BUILD_PLAN,
            ToolsHandler.GENERATE_CODE
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
        dir_path = path.dirname(file_path)
        if dir_path:
            makedirs(dir_path, exist_ok=True)
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
    
    async def build_plan(self, task:str, reasoning_effort:str, model:str) -> str:
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
        - write_file: Create/overwrite files
        - edit_file: Modify existing files
        - find_file: Search for files
        - execute_bash: Run shell commands
        - generate_code: Create code using specialized models
        - ask_for_help: Get assistance for complex problems
        - web_search: Search for current information
        - handle_loop: Manage iterative processes

        PLAN OUTPUT FORMAT:
        Structure your plan as a numbered list with:
        1. **Step Title** - Brief description
        - Detailed explanation of what needs to be done
        - Required tools: [tool_name1, tool_name2]
        - Expected outcome: What should result from this step
        - Dependencies: What must be completed before this step

        Include these sections:
        - **OVERVIEW**: High-level summary of the approach
        - **PREREQUISITES**: What needs to be verified before starting
        - **EXECUTION STEPS**: Detailed step-by-step plan
        - **VALIDATION**: How to verify successful completion
        - **POTENTIAL ISSUES**: Common problems and mitigation strategies

        REASONING APPROACH:
        - Think deeply about the problem space
        - Consider multiple approaches and choose the optimal one
        - Anticipate edge cases and failure scenarios
        - Plan for scalability and maintainability
        - Include testing and quality assurance steps
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
            max_completion_tokens=100_000,
            reasoning_effort=reasoning_effort
        )

        return response.choices[0].message.content
    
    async def generate_code(self, file_path:str, query:str, language:str, model:str, thinking_budget:int=1000, max_output_tokens:int=16384) -> str:
        dir_path = path.dirname(file_path)
        if dir_path:
            makedirs(dir_path, exist_ok=True)
        
        system_instruction = f"""
        You are an expert software engineer tasked with generating clean, production-ready {language} code.

        REQUIREMENTS:
        - Generate complete, syntactically correct {language} code
        - Include necessary imports, proper error handling, and clear variable names
        - Follow {language} best practices and standard formatting conventions
        - Wrap your code in a single code block using triple backticks with language specification

        CONTEXT UNDERSTANDING:
        - Analyze the file path to understand the intended purpose and structure
        - Consider the project structure and naming conventions
        - Generate code that integrates well with typical {language} project patterns

        OUTPUT FORMAT:
        ```{language}
        [your complete code here]
        ```
        The code should be production-ready and can be directly written to the specified file.
        """

        response = await self.gemini_client.aio.models.generate_content(
           model=model,
            contents=[
                genai.types.Content(
                    role="user",
                    parts=[
                        genai.types.Part(text=query)
                    ]
                )
            ],
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
                thinking_config=genai.types.ThinkingConfig(
                    thinking_budget=thinking_budget
                ),
                max_output_tokens=max_output_tokens
            )
        )
        
        # Extract code from markdown code block
        code_pattern = rf"```{re.escape(language)}\n(.*?)\n```"
        match = re.search(code_pattern, response.text, re.DOTALL)

        if match:
            source_code = match.group(1).strip()
        else:
            # Fallback: try to extract any code block
            fallback_pattern = r"```\w*\n(.*?)\n```"
            fallback_match = re.search(fallback_pattern, response.text, re.DOTALL)
            source_code = fallback_match.group(1).strip() if fallback_match else response.text.strip()
        
        with open(file_path, "w") as file:
            file.write(source_code)

        return f"File {file_path} was created"