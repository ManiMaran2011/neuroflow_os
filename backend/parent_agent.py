from agents.task_agent import TaskAgent
from agents.calendar_agent import CalendarAgent
from agents.research_agent import ResearchAgent
from agents.browser_agent import BrowserAgent
from agents.notification_agent import NotificationAgent
from agents.report_agent import ReportAgent
from agents.contact_agent import ContactAgent
from agents.energy_agent import EnergyAgent
from agents.xp_agent import XPAgent

class ParentAgent:
    def __init__(self):
        self.action_agents = [
            TaskAgent(),
            CalendarAgent(),
            NotificationAgent(),
            BrowserAgent(),
            ReportAgent(),
            ContactAgent(),
            EnergyAgent()
        ]
        self.research_agent = ResearchAgent()
        self.xp_agent = XPAgent()

    async def handle(self, user_input: str, execution_plan: dict | None = None):
        results = {}

        if execution_plan is None:
            research = await self.research_agent.run(user_input)
            return {
                "mode": "THINK",
                "results": {"ResearchAgent": research}
            }

        for agent in self.action_agents:
            if agent.name in execution_plan["agents"]:
                result = await agent.run(user_input)
                results[agent.name] = result

        xp_result = await self.xp_agent.reward()
        results["XPAgent"] = xp_result

        return {
            "mode": "ACT",
            "results": results
        }











