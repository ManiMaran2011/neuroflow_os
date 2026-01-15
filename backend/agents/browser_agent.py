from backend.agents.base_agent import BaseAgent


class BrowserAgent(BaseAgent):
    def __init__(self):
        super().__init__("BrowserAgent")

    async def run(self, user_input: str, params: dict) -> dict:
        return {
            "agent": self.name,
            "action": "browse",
            "result": f"Simulated browsing for: {user_input}"
        }



