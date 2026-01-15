from backend.agents.base_agent import BaseAgent

class ReportAgent(BaseAgent):
    name = "ReportAgent"

    async def run(self, user_input=None, params=None):
        return {
            "status": "simulated",
            "message": "Execution report generated"
        }




