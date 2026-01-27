from datetime import datetime
from backend.execution.agentss.evaluate_progress_agent import EvaluateProgressAgent


class MonitorAgent:
    """
    Long-running monitoring agent.
    Triggered daily via cron.
    """

    name = "MonitorAgent"

    async def run(self, user_input: str, params: dict) -> dict:
        """
        ParentAgent-compatible signature
        """

        tracked_goal = params.get("tracked_goal")
        execution_history = params.get("execution_history", [])
        now = params.get("now") or datetime.utcnow()

        if not tracked_goal:
            return {
                "agent": self.name,
                "action_needed": False,
                "reason": "No tracked goal found",
            }

        # 🔍 Evaluate progress using LLM
        evaluation = await EvaluateProgressAgent().run(
            plan=tracked_goal,
            execution_history=execution_history,
            now=now,
        )

        # -----------------------------------
        # DAILY CHECK-IN STRATEGY (Option C)
        # -----------------------------------
        # For now: always ask once per day
        # (Later: gate by time / streak / last response)

        return {
            "agent": self.name,
            "action_needed": True,
            "execution_channel": "email",
            "goal_id": tracked_goal["id"],
            "suggested_action": "Daily progress check-in",
            "reason": "Waiting for user confirmation",
        }

