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
        - "ask": Seeking user input, clarification, guidance, confirmation, or making inquiries  
        - "notify": General informational messages, explanations, or notifications
        - "confirm": Seeking user confirmation for a decision or action  
        - "analyze": Analyzing a situation, problem, or data (self-reflection)  
        - "update": Progress reports, status changes, or ongoing task information
        - "reply": Final results, completed work, conclusions, or task completion messages

        Typical Usage Patterns:
        - reply, ask, confirm are used for chatting with the user: this is an interactive mode => agent -> user -> agent
        - notify, think, update, analyze are used for long-running tasks: this is a autonomous mode => agent -> task -> agent -> task -> ... -> agent

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
                    "enum": ["think", "ask", "confirm", "analyze" ,"notify", "update", "reply"],
                    "default": "reply",
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

SEARCH_THROUGH_WEB = {
    "type": "function",
    "function": {
        "name": "search_through_web",
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
       Create comprehensive, actionable execution plans for complex tasks using advanced reasoning models.
       
       This function provides:
       - Strategic breakdown of complex tasks into logical, sequential steps
       - Detailed analysis of dependencies, constraints, and potential failure points
       - Consideration of available tools and resource requirements
       - Adaptive planning that can incorporate lessons from previous attempts
       - Structured output with step priorities and detailed descriptions
       - Advanced reasoning capabilities for complex problem-solving scenarios
       
       Planning Capabilities:
       - Multi-step workflow design and coordination
       - Risk assessment and error handling strategies
       - Resource allocation and tool selection guidance
       - Timeline and dependency management
       - Iterative refinement when initial plans prove inadequate
       
       When to use:
       - Complex tasks requiring multiple tools and coordination
       - Research projects with unclear scope or methodology
       - Technical implementations with many dependencies
       - When previous approaches have failed and replanning is needed
       - Multi-phase projects requiring systematic execution
       
       Model Selection Guide:
       - o3: Most complex tasks requiring deep reasoning and novel problem-solving
       - o3-mini: Moderate complexity tasks with clear structure
       - o4-mini: Cutting-edge reasoning for the most demanding analytical tasks
       
       For replanning: Include context about previous attempts, what failed, and lessons learned in the task description.
       """,
       "parameters": {
           "type": "object",
           "properties": {
               "task": {
                   "type": "string", 
                   "description": "The task to build a plan for. Include context about previous attempts, constraints, requirements, and any specific guidance for replanning scenarios."
               },
               "reasoning_effort": {
                   "type": "string", 
                   "enum": ["low", "medium", "high"], 
                   "default": "medium",
                   "description": "Level of reasoning depth: low for simple tasks, medium for standard planning, high for complex multi-faceted problems requiring deep analysis."
               },
               "model": {
                   "type": "string", 
                   "enum": ["o3", "o3-mini", "o4-mini"],
                   "description": "Reasoning model to use based on task complexity and requirements."
               }
           },
           "required": ["task", "reasoning_effort", "model"]
       }
   }
}

APPLY_REGEX = {
    "type": "function",
    "function": {
        "name": "apply_regex",
        "description": """
        Apply regex pattern substitution to modify file content with precise pattern matching.
        This function provides:
        - Powerful pattern-based find and replace operations
        - Support for regex flags (IGNORECASE, MULTILINE, DOTALL, etc.)
        - Limited or unlimited substitution counts
        - Safe atomic file operations
        
        Use this when you need sophisticated pattern matching beyond simple string replacement on existing files.
        The agent should first read the file to understand its structure before applying regex modifications.
        This function is using python regex library under the hood.(import re)
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to modify"
                },
                "pattern": {
                    "type": "string", 
                    "description": "Regex pattern to match. Use raw strings for complex patterns."
                },
                "replacement": {
                    "type": "string",
                    "description": "Replacement string. Can include capture groups like \\1, \\2, etc."
                },
                "flags": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["IGNORECASE", "MULTILINE", "DOTALL", "VERBOSE", "ASCII", "LOCALE"]},
                    "description": "List of regex flags to apply"
                },
                "count": {
                    "type": "integer",
                    "default": 0,
                    "description": "Maximum number of substitutions to make. 0 means replace all occurrences."
                }
            },
            "required": ["file_path", "pattern", "replacement"]
        }
    }
}

