import json
from ..tools.base import BaseTool

class WebSearcher(BaseTool):
    def __init__(self, openai_client):
        self.openai_client = openai_client
    
    async def execute(self, query: str, model: str = "gpt-4o-mini-search-preview", 
                     search_context_size: str = "low", max_tokens: int = 1024) -> str:
        response = await self.openai_client.chat.completions.create(
            model=model,
            web_search_options={"search_context_size": search_context_size},
            messages=[{"role": "user", "content": query}],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content