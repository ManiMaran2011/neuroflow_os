from backend.agents.calendar_agent import CalendarAgent
from backend.agents.notification_agent import NotificationAgent
from backend.agents.task_agent import TaskAgent
from backend.agents.report_agent import ReportAgent
from backend.agents.xp_agent import XPAgent
from backend.execution.agentss.notify_agent import NotifyAgent


AGENT_REGISTRY = {
    "CalendarAgent": CalendarAgent,
    "NotificationAgent": NotificationAgent,
    "TaskAgent": TaskAgent,
    "ReportAgent": ReportAgent,
    "XPAgent": XPAgent,
    "NotifyAgent": NotifyAgent,
}


def get_agent_instances(agent_names):
    agents = []

    for name in agent_names:
        if name not in AGENT_REGISTRY:
            raise ValueError(f"Agent not registered: {name}")

        agents.append(AGENT_REGISTRY[name]())

    return agents






