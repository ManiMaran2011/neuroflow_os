from backend.agents.base_agent import BaseAgent

class TaskAgent(BaseAgent):
    name = "TaskAgent"

    async def run(self, user_input=None, params=None):
        return {
            "status": "simulated",
            "message": "Task created successfully"
        }





