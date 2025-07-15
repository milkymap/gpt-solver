ECHO = {
    "type": "function",
    "function": {
        "name": "echo",
        "description": """
        Display a message to the user for status updates, progress reports, or communication during task execution.
        This function provides a way to:
        - Show progress updates during long-running tasks
        - Display status messages to keep users informed
        - Provide feedback about task completion or errors
        - Send informational messages during execution flow
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            }
        }, 
        "required": ["message"]
    }
}

READ_FILE = {
    "type": "function",
    "function": {
        "name": "read_file", 
        "description": """
        Read and return the complete content of a file from the filesystem.
        This function allows:
        - Reading text files of any format
        - Accessing file contents for processing
        - Loading configuration files, data files, or code files
        - Throws FileNotFoundError if file doesn't exist
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"}
            }
        }, 
        "required": ["file_path"]
    }
}

WRITE_FILE = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": """
        Create a new file or overwrite an existing file with the specified content.
        This function provides:
        - Automatic creation of parent directories if they don't exist
        - Complete overwrite of existing files
        - Creation of new files in specified path
        - Support for writing any text content
        - Full path handling with proper directory creation
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "content": {"type": "string"}
            }
        }, 
        "required": ["file_path", "content"]
    }
}

WEB_SEARCH = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": """
        Search the internet for current information using AI-powered web search.
        This function enables:
        - Real-time information gathering from the web
        - Access to current documentation and resources
        - Research on libraries and best practices
        - Retrieval of up-to-date data and knowledge
        - Configurable search depth and response length
        - Choice between different search models for optimal results
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "model": {"type": "string", "enum": ["gpt-4o-mini-search-preview", "gpt-4o-search-preview"], "default": "gpt-4o-mini-search-preview"},
                "search_context_size": {"type": "string", "enum": ["low", "medium", "high"], "default": "medium"},
                "max_tokens": {"type": "integer", "default": 1024}
            }
        }, 
        "required": ["query"]
    }
}

EXECUTE_BASH = {
    "type": "function",
    "function": {
        "name": "execute_bash",
        "description": """
        Execute a bash command and return the complete execution results.
        This function provides:
        - Command execution in shell environment
        - Capture of stdout and stderr outputs
        - Return code from command execution
        - Support for any valid bash command
        - Full shell command execution capabilities
        - Error handling and output collection
        - Timeout support for long-running commands
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "timeout": {"type": "integer", "default": 30}
            }
        }, 
        "required": ["command"]
    }
}

GENERATE_CODE = {
    "type": "function",
    "function": {
        "name": "generate_code",
        "description": """
        Generate code based on a given query and return the complete source code.
        This function provides:
        - Code generation based on natural language queries
        - Support for any programming language
        - Generation of complete source code files
        - Support for any valid programming language
        - Full code generation capabilities
        - Use gemini 2.5 pro for complex tasks
        - Use gemini 2.5 flash for simple tasks (realy fast)
        - max output tokens should be between 8192 and 16384
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "The path to the file to generate code for"},
                "query": {"type": "string", "description": "The query to generate code for, should be a very detailed description"},
                "language": {"type": "string", "description": "The programming language to use for code generation"},
                "model": {"type": "string", "enum": ["gemini-2.5-pro", "gemini-2.5-flash"]},
                "thinking_budget": {"type": "integer", "default": 1000, "description": "The budget for the thinking process, choose a value between 1000 and 3000"},
                "max_output_tokens": {"type": "integer", "default": 16384, "description": "The maximum number of tokens to generate in the output, can go up to 16384"}
            }
        },
        "required": ["file_path", "query", "model"],
    }
}

BUILD_PLAN = {
    "type": "function",
    "function": {
        "name": "build_plan",
        "description": """
        Build a plan for a given task and return the complete plan.
        This function provides:
        - Plan generation based on natural language tasks
        - Support for any task
        - Generation of complete plans
        - Support for any valid task
        - Full plan generation capabilities
        - Use o3 for complex tasks
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "The task to build a plan for"},
                "reasoning_effort": {"type": "string", "enum": ["low", "medium", "high"], "default": "medium"},
                "model": {"type": "string", "enum": ["o3", "o3-mini", "o4", "o3-mini-high"]}
            }
        },
        "required": ["task", "reasoning_effort", "model"]
    }
}