import json
import subprocess
from ..tools.base import BaseTool

class BashExecutor(BaseTool):
    async def execute(self, command: str, timeout: int = 10) -> str:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=timeout
        )
        return json.dumps({
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }, indent=3)