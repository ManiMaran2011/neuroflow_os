from datetime import datetime
from backend.execution.agentss.evaluate_progress_agent import EvaluateProgressAgent


class MonitorAgent:
    name = "MonitorAgent"

    async def run(self, user_input: str, params: dict) -> dict:
        tracked_goal = params["tracked_goal"]

        execution_history = params.get("execution_history", [])
        now = params.get("now") or datetime.utcnow()

        evaluation = await EvaluateProgressAgent().run(
            plan=tracked_goal,
            execution_history=execution_history,
            now=now,
        )

        if evaluation["action_needed"]:
            return {
                "agent": self.name,
                "action_needed": True,
                "execution_channel": evaluation["execution_channel"],
                "suggested_action": evaluation["suggested_action"],
                "reason": evaluation["reason"],
            }

        return {
            "agent": self.name,
            "action_needed": False,
            "status": "on_track",
        }

