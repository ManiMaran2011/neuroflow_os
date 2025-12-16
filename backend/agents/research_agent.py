from ..base_agent import BaseAgent
from ..utils.llm import ask_llm

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__("research_db.json", "ResearchAgent")

    async def run(self, instruction: str):
        response = await ask_llm(instruction)
        return response

