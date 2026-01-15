from backend.agents.base_agent import BaseAgent


class ContactAgent(BaseAgent):
    def __init__(self):
        super().__init__("ContactAgent")

    async def run(self, user_input: str, params: dict) -> dict:
        return {
            "agent": self.name,
            "action": "manage_contact",
            "contact": params
        }



