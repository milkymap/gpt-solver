import json
from rich import print as rprint
from rich.panel import Panel
from rich.text import Text

class MessageFormatter:
    def __init__(self, default_print_mode: str = "rich"):
        self.default_print_mode = default_print_mode
        self.type_colors = {
            "think": "bold blue",
            "ask": "bold yellow",
            "confirm": "bold magenta",
            "analyze": "bold cyan",
            "notify": "bold green",
            "update": "bold white",
            "reply": "bold"
        }
    
    def format_message(self, message: str, message_type: str, internal_state: int) -> str:
        if self.default_print_mode == "rich":
            color = self.type_colors.get(message_type, "bold")
            title = f"{message_type.upper()}"
            rprint(Panel(
                Text(message, style=color),
                title=title,
                title_align="left",
                border_style=color,
                padding=(1, 2)
            ))
        else:
            print(message)
        return json.dumps({
            "message": message,
            "message_type": message_type,
            "agent_loop_state": "interactive" if internal_state == 0 else "autonomous"
        }, indent=3)