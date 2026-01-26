import uuid
from datetime import datetime, timedelta

from backend.llm_planner import create_plan_with_llm


# =====================================================
# RULE-BASED FALLBACK PLANNER
# =====================================================

async def create_plan_rule_based(user_input: str) -> dict:
    text = user_input.lower()

    SCHEDULE_WORDS = ["schedule", "set up", "add", "create", "book", "plan"]
    REMINDER_WORDS = ["remind", "reminder", "notify", "alert"]
    MEETING_WORDS = ["meeting", "call", "event", "appointment", "session"]
    TASK_WORDS = ["task", "workout", "gym", "exercise", "todo", "to do"]
    TIME_WORDS = ["tomorrow", "today", "pm", "am", "at"]

    if (
        any(w in text for w in SCHEDULE_WORDS)
        or any(w in text for w in REMINDER_WORDS)
    ):
        agents = ["TaskAgent"]

        if any(w in text for w in REMINDER_WORDS):
            agents.append("NotificationAgent")

        if (
            any(w in text for w in MEETING_WORDS)
            or any(w in text for w in TASK_WORDS)
            or any(w in text for w in TIME_WORDS)
        ):
            agents.append("CalendarAgent")

        agents.extend(["ReportAgent", "XPAgent"])

        start = datetime.utcnow() + timedelta(days=1)
        end = start + timedelta(hours=1)

        return {
            "plan_id": str(uuid.uuid4()),
            "intent": "task_with_reminder",
            "actions": [
                "create_task",
                "schedule_reminder",
                "create_calendar_event",
            ],
            "agents": agents,
            "params": {
                "raw_input": user_input,
                "title": "NeuroFlow Task / Event",
                "start": start.isoformat(),
                "end": end.isoformat(),
                "reminder_time": (start - timedelta(hours=1)).isoformat(),
                "user_email": "<AUTO FILLED IN ask_routes>",
                "google_token": "<AUTO FILLED IN ask_routes>",
            },
            "priority": "medium",
            "confidence": 0.7,
            "reasoning": "Rule-based planner matched scheduling/reminder intent",
            "requires_approval": True,
            "created_at": datetime.utcnow().isoformat(),
        }

    return {
        "plan_id": str(uuid.uuid4()),
        "intent": "unknown",
        "actions": [],
        "agents": ["ReportAgent"],
        "params": {"raw_input": user_input},
        "priority": "low",
        "confidence": 0.2,
        "reasoning": "No confident rule-based match",
        "requires_approval": False,
        "created_at": datetime.utcnow().isoformat(),
    }


# =====================================================
# MAIN PLANNER ENTRYPOINT (USED BY ROUTES)
# =====================================================

async def create_plan(user_input: str) -> dict:
    """
    Primary planner entrypoint.
    1. Try LLM planner
    2. Normalize output
    3. Fallback to rule-based planner if LLM fails
    """
    try:
        llm_plan = await create_plan_with_llm(user_input)

        # ---------------- NORMALIZE LLM PLAN ----------------

        return {
            "plan_id": str(uuid.uuid4()),
            "intent": "llm_routed_execution",
            "actions": [llm_plan.get("execution_channel")],
            "agents": ["LLMPlanner", "CalendarAgent"]
            if llm_plan.get("execution_channel") == "calendar"
            else ["LLMPlanner"],
            "params": {
                "raw_input": user_input,
                "action": llm_plan.get("action"),
            },
            "priority": "medium",
            "confidence": llm_plan.get("confidence", 0.95),
            "reasoning": "LLM planner selected execution strategy",
            "requires_approval": llm_plan.get("requires_approval", False),
            "created_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        print("⚠️ LLM planner failed, falling back:", e)
        return await create_plan_rule_based(user_input)














