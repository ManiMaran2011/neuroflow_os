# backend/safety/policy_engine.py

from fastapi import HTTPException
from datetime import datetime


class PolicyEngine:
    """
    Lightweight safety & validation layer.
    Blocks invalid or unsafe execution plans.
    """

    @staticmethod
    def enforce(execution_plan: dict):
        """
        Raises HTTPException if execution should be blocked.
        """

        if not execution_plan:
            raise HTTPException(
                status_code=400,
                detail="Empty execution plan"
            )

        actions = execution_plan.get("actions", [])

        # Example rule: no actions = nothing to do
        if not actions:
            raise HTTPException(
                status_code=400,
                detail="No executable actions in plan"
            )

        # Example rule: calendar events must be future-dated
        if "create_calendar_event" in actions:
            params = execution_plan.get("params", {})
            start = params.get("start")

            if start:
                start_dt = datetime.fromisoformat(start)
                if start_dt < datetime.utcnow():
                    raise HTTPException(
                        status_code=400,
                        detail="Cannot create calendar event in the past"
                    )

        # If no rules triggered → allow execution
        return True

