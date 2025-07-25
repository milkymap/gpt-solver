class EngineState:
    """Manages the internal state of the agent's execution loop."""
    
    def __init__(self):
        self.internal_state = 0  # 0: interactive, 1: autonomous
        
    def update_from_message_type(self, message_type: str):
        if message_type in {"reply", "ask", "confirm"}:
            self.internal_state = 0
        elif message_type in {"notify", "think", "update", "analyze"}:
            self.internal_state = 1
        else:
            raise ValueError(f"Invalid message type: {message_type}")