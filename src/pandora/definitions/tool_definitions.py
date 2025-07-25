def get_core_tools(default_print_mode: str) -> list:
    print_message = {
        "type": "function",
        "function": {
            "name": "print_message",
            "description": "Display a message to the user and control agent execution flow",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "message_type": {
                        "type": "string",
                        "enum": ["think", "ask", "confirm", "analyze", "notify", "update", "reply"],
                        "default": "reply"
                    },
                    "print_mode": {
                        "type": "string",
                        "enum": ["json", "rich"],
                        "default": default_print_mode
                    }
                },
                "required": ["message", "message_type"]
            }
        }
    }
    read_file = {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read and return the complete content of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"}
                },
                "required": ["file_path"]
            }
        }
    }
    create_file = {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Create or overwrite a file with specified content",
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
    edit_file = {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Modify file content using natural language instructions",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "edit_instructions": {"type": "string"},
                    "context": {"type": "string", "default": ""},
                    "model": {"type": "string", "enum": ["gpt-4.1", "gpt-4.1-mini"], "default": "gpt-4.1"}
                },
                "required": ["file_path", "edit_instructions"]
            }
        }
    }
    search_through_web = {
        "type": "function",
        "function": {
            "name": "search_through_web",
            "description": "Perform web search and return summarized results",
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
    execute_bash = {
        "type": "function",
        "function": {
            "name": "execute_bash",
            "description": "Execute bash command and return results",
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
    generate_plan = {
        "type": "function",
        "function": {
            "name": "generate_plan",
            "description": "Create detailed execution plan for complex tasks",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "string"},
                    "reasoning_effort": {"type": "string", "enum": ["low", "medium", "high"], "default": "medium"},
                    "model": {"type": "string", "enum": ["o3", "o3-mini", "o4-mini"]}
                },
                "required": ["task", "model"]
            }
        }
    }
    apply_regex = {
        "type": "function",
        "function": {
            "name": "apply_regex",
            "description": "Apply regex pattern to modify file content",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "pattern": {"type": "string"},
                    "replacement": {"type": "string"},
                    "flags": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["IGNORECASE", "MULTILINE", "DOTALL", "VERBOSE", "ASCII", "LOCALE"]
                        }
                    },
                    "count": {"type": "integer", "default": 0}
                },
                "required": ["file_path", "pattern", "replacement"]
            }
        }
    }
    return [
        print_message,
        read_file,
        create_file,
        edit_file,
        search_through_web,
        execute_bash,
        generate_plan,
        apply_regex
    ]