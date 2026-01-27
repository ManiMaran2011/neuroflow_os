import uuid
from datetime import datetime, timedelta

from backend.llm_planner import create_plan_with_llm


async def create_plan(user_input: str) -> dict:
    text = user_input.lower()

    is_tracking = any(
        w in text
        for w in ["track", "monitor", "progress", "daily", "every day", "7 days"]
    )

    try:
        llm_plan = await create_plan_with_llm(user_input)
    except Exception:
        llm_plan = {}

    plan = {
        "plan_id": str(uuid.uuid4()),
        "intent": "llm_routed_execution",
        "actions": [],
        "agents": ["LLMPlanner"],
        "params": {
            "raw_input": user_input,
        },
        "priority": "medium",
        "confidence": llm_plan.get("confidence", 0.9),
        "reasoning": "Planner selected execution strategy",
        "requires_approval": False,
        "created_at": datetime.utcnow().isoformat(),
    }

    # 🔥 HARD RULE: tracking ⇒ tracked_goal
    if is_tracking:
        plan["intent"] = "TRACK_GOAL"
        plan["agents"].append("MonitorAgent")

        plan["tracked_goal"] = {
            "id": str(uuid.uuid4()),
            "metric": "generic_progress",
            "frequency": "daily",
            "duration_days": 7,
            "created_at": datetime.utcnow().isoformat(),
            "cron": "0 6 * * *",
        }

    return plan















