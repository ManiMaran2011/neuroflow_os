import uuid
from datetime import datetime
from backend.llm_planner import create_plan_with_llm


# =====================================================
# MAIN PLANNER ENTRYPOINT
# =====================================================

async def create_plan(user_input: str) -> dict:
    """
    Authoritative planner.
    Produces a fully-resolved execution plan.
    """

    text = user_input.lower()

    # -----------------------------------------
    # INTENT HEURISTICS (HARD RULES)
    # -----------------------------------------

    is_tracking = any(
        w in text
        for w in ["track", "monitor", "progress", "daily", "every day", "7 days"]
    )

    is_calendar = any(
        w in text
        for w in ["schedule", "meeting", "calendar", "book", "appointment"]
    )

    # -----------------------------------------
    # DEFAULT PLAN SHELL
    # -----------------------------------------

    plan = {
        "plan_id": str(uuid.uuid4()),
        "intent": "generic_execution",
        "execution_type": "instant_task",   # 👈 DEFAULT (IMPORTANT)
        "execution_channel": None,
        "agents": [],
        "actions": [],
        "params": {
            "raw_input": user_input
        },
        "priority": "medium",
        "confidence": 0.9,
        "requires_approval": True,
        "created_at": datetime.utcnow().isoformat(),
    }

    # -----------------------------------------
    # 1️⃣ TRACKING / HABIT / FITNESS
    # -----------------------------------------

    if is_tracking:
        plan["intent"] = "TRACK_GOAL"
        plan["execution_type"] = "tracking"

        # REAL + SHOW agents
        plan["agents"] = [
            "CalendarAgent",    # real (optional reminders)
            "MonitorAgent",     # real (cron-based)
            "NotifyAgent",      # real (email / slack)
            "TaskAgent",        # show
            "ReportAgent",      # show
            "XPAgent"           # real
        ]

        plan["params"].update({
            "execution_type": "tracking",
            "frequency": "daily",
            "duration_days": 7
        })

        return plan

    # -----------------------------------------
    # 2️⃣ ONE-TIME SCHEDULING (MEETINGS)
    # -----------------------------------------

    if is_calendar:
        plan["intent"] = "SCHEDULE_EVENT"
        plan["execution_type"] = "instant_task"
        plan["execution_channel"] = "calendar"

        plan["agents"] = [
            "CalendarAgent",   # 🔥 REAL SIDE EFFECT
            "ReportAgent",     # show
            "TaskAgent",       # show
            "NotifyAgent",     # show (email confirmation)
            "XPAgent"          # real
        ]

        plan["actions"] = ["create_calendar_event"]

        return plan

    # -----------------------------------------
    # 3️⃣ FALLBACK → LLM-ROUTED EXECUTION
    # -----------------------------------------

    try:
        llm_plan = await create_plan_with_llm(user_input)

        plan.update({
            "intent": llm_plan.get("intent", "llm_execution"),
            "execution_type": llm_plan.get("execution_type", "instant_task"),
            "execution_channel": llm_plan.get("execution_channel"),
            "agents": llm_plan.get("agents", []) + ["XPAgent"],
            "params": {
                **plan["params"],
                **llm_plan.get("params", {})
            },
            "requires_approval": llm_plan.get("requires_approval", True),
            "confidence": llm_plan.get("confidence", 0.85)
        })

        return plan

    except Exception as e:
        # -------------------------------------
        # SAFETY FALLBACK
        # -------------------------------------
        return {
            "plan_id": str(uuid.uuid4()),
            "intent": "fallback_task",
            "execution_type": "instant_task",
            "agents": [
                "TaskAgent",
                "ReportAgent",
                "XPAgent"
            ],
            "params": {
                "raw_input": user_input,
                "error": str(e)
            },
            "requires_approval": True,
            "created_at": datetime.utcnow().isoformat(),
        }
















