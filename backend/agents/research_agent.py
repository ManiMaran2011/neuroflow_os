from backend.agents.base_agent import BaseAgent


class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__("ResearchAgent")

    async def run(self, user_input: str, params: dict) -> dict:
        return {
            "agent": self.name,
            "action": "research",
            "summary": f"Research summary for: {user_input}"
        }




