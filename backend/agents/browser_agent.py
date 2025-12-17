from base_agent import BaseAgent

class BrowserAgent(BaseAgent):
    name = "BrowserAgent"

    def __init__(self):
        self.db_path = None

    async def run(self, user_input: str):
        return {
            "agent": self.name,
            "status": "success",
            "message": "Browser lookup simulated",
            "data": {
                "query": user_input
            }
        }


