from backend.agents.base_agent import BaseAgent

class XPAgent(BaseAgent):
    name = "XPAgent"

    async def run(self, user_input=None, params=None):
        return {
            "status": "simulated",
            "message": "XP awarded to user"
        }







