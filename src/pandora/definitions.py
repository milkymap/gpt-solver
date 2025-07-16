PRINT_MESSAGE ={
    "type": "function",
    "function": {
        "name": "print_message",
        "description": """
        Display a message to the user and control agent execution flow. This function serves dual purposes:
        
        Communication:
        - Show progress updates during long-running tasks
        - Display status messages to keep users informed
        - Provide feedback about task completion or errors
        - Send informational messages during execution flow
        - Log reasoning steps and decision points for trajectory tracking
        
        Execution Control:
        - Explicitly control whether the agent continues processing or terminates
        - Provide deterministic loop control with transparent termination conditions
        - Enable clean handoff between parent and child agents in fork scenarios
        - Ensure all stopping points are conscious decisions recorded in trajectory history
        
        Every call to this function represents a decision point where the agent must choose to either continue working or return control to its parent/caller.
        Display a message to the user and control agent execution flow with explicit message typing.
        
        Message Types:
        - "think": Internal reasoning, planning, analysis, or decision-making processes
        - "question": Seeking user input, clarification, guidance, confirmation, or making inquiries  
        - "notify": General informational messages, explanations, or notifications
        - "update": Progress reports, status changes, or ongoing task information
        - "reply": Final results, completed work, conclusions, or task completion messages

        Typical Usage Patterns:
        - reply and question are used for chatting with the user: this is an open-loop mode => agent -> user -> agent
        - notify, think, update are used for long-running tasks: this is a closed-loop mode => agent -> task -> agent -> task -> ... -> agent

        choose carefully the message type to use.
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The message content to display. Becomes part of the agent's trajectory log and is searchable in git history for pattern analysis."
                },
                "message_type": {
                    "type": "string",
                    "enum": ["think", "question", "notify", "update", "reply"],
                    "default": "info",
                    "description": "The type of message to display. It will be used to determine the message type and the way to display it to the user."
                }
            }, 
            "required": ["message", "message_type"]
        }
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
            },
            "required": ["file_path"]
        }
    }
}

CREATE_FILE = {
    "type": "function",
    "function": {
        "name": "create_file",
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
            },
            "required": ["file_path", "content"]
        }
    }
}

EDIT_FILE = {
   "type": "function",
   "function": {
       "name": "edit_file",
       "description": """
       Intelligently modify existing files using natural language instructions and contextual understanding.
       This function provides:
       - Semantic understanding of file content and structure
       - Context-aware modifications that preserve meaning and relationships
       - Support for any text-based file format (code, documentation, configuration, data files)
       - Intelligent preservation of formatting, style, and structural patterns
       - Validation of file existence and content coherence before updates
       - Atomic update operation (all changes applied successfully or none)
       - Natural language instruction processing for complex transformations
       - Contextual awareness to maintain consistency with broader project/document structure
       
       Examples of supported operations:
       - Content restructuring and reorganization
       - Adding, removing, or modifying sections
       - Style and formatting adjustments
       - Data transformations and corrections
       - Template customization and parameter updates
       - Documentation updates and improvements

       IMPORTANT:
       - choose carefully the model to use.
       - both are realy good at following the instructions, so be clear and specific.
       - both model has 1M tokens context window, they can process large files.
       - use gpt-4.1 for complex task such as code editing, documentation, etc.
       - use gpt-4.1-mini for simple task such as configuration, data, etc.
       """,
       "parameters": {
           "type": "object",
           "properties": {
               "file_path": {
                   "type": "string",
                   "description": "Path to the file to be edited"
               },
               "edit_instructions": {
                   "type": "string", 
                   "description": "Natural language description of the desired changes. Be specific about what to modify, add, remove, or restructure."
               },
               "context": {
                   "type": "string",
                   "description": "Additional context about the file purpose, related files, project structure, formatting requirements, or any other relevant information that will help make better editing decisions."
               }, 
               "model": {"type": "string", "enum": ["gpt-4.1", "gpt-4.1-mini"], "default": "gpt-4.1"}
           },
           "required": ["file_path", "edit_instructions"]
       } 
   }
}

SEARCH_THROUGH_INTERNET = {
    "type": "function",
    "function": {
        "name": "search_through_internet",
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
            },
            "required": ["query"]
        }
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
            },
            "required": ["command"]
        }
    }
}

GENERATE_PLAN = {
    "type": "function",
    "function": {
        "name": "generate_plan",
        "description": """
        Build a plan for a given task and return the complete plan.
        This function provides:
        - Plan generation based on natural language tasks
        - Support for any task
        - Generation of complete plans
        - Support for any valid task
        - Full plan generation capabilities
        - Use o3 for complex tasks
        return a sequence of steps to complete the task
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "The task to build a plan for"},
                "reasoning_effort": {"type": "string", "enum": ["low", "medium", "high"], "default": "medium"},
                "model": {"type": "string", "enum": ["o3", "o3-mini", "o4", "o3-mini-high"]}
            },
            "required": ["task", "reasoning_effort", "model"]
        }
    }
}

