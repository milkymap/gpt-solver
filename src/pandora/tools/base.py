from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        pass