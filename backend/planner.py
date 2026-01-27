import uuid
from datetime import datetime

from backend.llm_planner import create_plan_with_llm


async def create_plan(user_input: str) -> dict:
    text = user_input.lower()

    # ----------------------------------
    # RULE-BASED TRACKING DETECTION
    # ----------------------------------
    is_tracking = any(
        w in text
        for w in [
            "track",
            "monitor",
            "progress",
            "daily",
            "every day",
            "habit",
            "routine",
            "7 days",
        ]
    )

    # ----------------------------------
    # TRY LLM PLANNER (OPTIONAL)
    # ----------------------------------
    try:
        llm_plan = await create_plan_with_llm(user_input)
    except Exception:
        llm_plan = {}

    # ----------------------------------
    # BASE PLAN (SAFE DEFAULT)
    # ----------------------------------
    plan = {
        "plan_id": str(uuid.uuid4()),
        "intent": llm_plan.get("intent", "agentic_execution"),
        "execution_type": llm_plan.get("execution_type"),  # may be None
        "actions": [],
        "agents": ["LLMPlanner"],
        "params": {
            "raw_input": user_input,
        },
        "priority": "medium",
        "confidence": llm_plan.get("confidence", 0.9),
        "reasoning": "Planner selected execution strategy",
        "requires_approval": llm_plan.get("requires_approval", False),
        "created_at": datetime.utcnow().isoformat(),
    }

    # ----------------------------------
    # 🔥 HARD OVERRIDE: TRACKING GOALS
    # ----------------------------------
    if is_tracking:
        plan["intent"] = "TRACK_GOAL"

        # 🔥 THIS IS THE CRITICAL LINE
        plan["execution_type"] = "tracked_goal"

        plan["agents"] = ["MonitorAgent"]

        plan["schedule"] = {
            "frequency": "daily",
            "time": "21:00",  # logical default (cron decides actual trigger)
            "duration_days": 7,
        }

        plan["tracked_goal"] = {
            "id": str(uuid.uuid4()),
            "metric": "generic_progress",
            "frequency": "daily",
            "duration_days": 7,
            "created_at": datetime.utcnow().isoformat(),
        }

    return plan















