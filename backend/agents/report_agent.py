from ..base_agent import BaseAgent

class ReportAgent(BaseAgent):
    def __init__(self):
        super().__init__("report_db.json", "ReportAgent")

    async def run(self, instruction: str):
        return "Weekly report generated"

