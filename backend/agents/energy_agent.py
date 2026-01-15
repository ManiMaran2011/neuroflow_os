from backend.agents.base_agent import BaseAgent


class EnergyAgent(BaseAgent):
    def __init__(self):
        super().__init__("EnergyAgent")

    async def run(self, user_input: str, params: dict) -> dict:
        return {
            "agent": self.name,
            "action": "analyze_energy",
            "status": "Energy usage analyzed (mock)"
        }



