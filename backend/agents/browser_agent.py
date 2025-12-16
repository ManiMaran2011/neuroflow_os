from ..base_agent import BaseAgent

class BrowserAgent(BaseAgent):
    def __init__(self):
        super().__init__("browser_db.json", "BrowserAgent")

    async def run(self, instruction: str):
        return f"Browser lookup simulated for: {instruction}"
