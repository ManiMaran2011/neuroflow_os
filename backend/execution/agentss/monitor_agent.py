from datetime import datetime, timedelta
from typing import List, Dict, Optional


class MonitorAgent:
    """
    MonitorAgent observes long-running plans over time
    and decides whether further action is needed.
    """

    name = "MonitorAgent"

    async def run(
        self,
        plan: Dict,
        execution_history: List[Dict],
        now: Optional[datetime] = None,
    ) -> Dict:
        """
        Args:
            plan: stored execution plan
            execution_history: past executions for this plan
            now: injected time (for testing / cron)
        Returns:
            decision dict
        """

        now = now or datetime.utcnow()

        created_at = datetime.fromisoformat(plan["created_at"])
        days_elapsed = (now - created_at).days + 1

        # -----------------------------------
        # 1️⃣ Derive progress signals
        # -----------------------------------

        completed_actions = [
            e for e in execution_history
            if e.get("status") == "completed"
        ]

        last_execution = (
            max(
                execution_history,
                key=lambda e: e.get("created_at"),
                default=None,
            )
            if execution_history
            else None
        )

        days_since_last_action = None
        if last_execution:
            last_time = datetime.fromisoformat(last_execution["created_at"])
            days_since_last_action = (now - last_time).days

        # -----------------------------------
        # 2️⃣ Simple progress heuristics (v1)
        # -----------------------------------

        # Expected: one action per day
        expected_actions = days_elapsed
        actual_actions = len(completed_actions)

        behind = actual_actions < expected_actions - 1

        # -----------------------------------
        # 3️⃣ Decision logic
        # -----------------------------------

        if not behind:
            return {
                "agent": self.name,
                "action_needed": False,
                "status": "on_track",
                "reason": "User is progressing as expected",
            }

        # User inactive for too long
        if days_since_last_action is not None and days_since_last_action >= 2:
            return {
                "agent": self.name,
                "action_needed": True,
                "decision": "check_in",
                "execution_channel": "slack",
                "reason": "User has been inactive for multiple days",
                "suggested_action": "Send a gentle progress check-in",
            }

        # Fallback: wait
        return {
            "agent": self.name,
            "action_needed": False,
            "status": "waiting",
            "reason": "No immediate intervention required",
        }
