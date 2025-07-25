from ..tools.base import BaseTool

class PlanGenerator(BaseTool):
    def __init__(self, openai_client):
        self.openai_client = openai_client
    
    async def execute(self, task: str, reasoning_effort: str, model: str) -> str:
        system_instruction = "You are an expert task planner. Create comprehensive, actionable execution plans."
        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Task: {task}"}
            ],
            max_tokens=100_000
        )
        return response.choices[0].message.content