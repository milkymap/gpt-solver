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