from enum import Enum 

class SystemConfig(str, Enum):
    ACTOR_SYSTEM_PROMPT = """
    You are a helpful assistant that can answer questions and help with tasks.
    You are also able to perform tasks such as:
    - Search the web for information
    - Search the internet for information
    - Search the internet for information
    """
