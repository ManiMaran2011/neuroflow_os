from agents.task_agent import TaskAgent
from agents.calendar_agent import CalendarAgent
from agents.research_agent import ResearchAgent
from agents.browser_agent import BrowserAgent
from agents.xp_agent import XPAgent
from agents.report_agent import ReportAgent
from agents.contact_agent import ContactAgent
from agents.notification_agent import NotificationAgent
from agents.energy_agent import EnergyAgent

from utils.router import classify_intent
from utils.paei import compute_paei_weights


class ParentAgent:
    def __init__(self):
        self.agents = [
            TaskAgent(),
            CalendarAgent(),
            ResearchAgent(),
            BrowserAgent(),
            XPAgent(),
            ReportAgent(),
            ContactAgent(),
            NotificationAgent(),
            EnergyAgent(),
        ]

    async def handle(self, user_input: str):
        results = {}

        for agent in self.agents:
            try:
                output = await agent.run(user_input)
                results[agent.name] = output
            except Exception as e:
                results[agent.name] = {
                    "agent": agent.name,
                    "status": "error",
                    "message": str(e)
                }

        return compute_paei_weights(user_input, results)







