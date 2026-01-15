import uuid
from datetime import datetime, timedelta


async def create_plan(user_input: str) -> dict:
    text = user_input.lower()

    # -----------------------------
    # KEYWORD GROUPS (RULE-BASED)
    # -----------------------------
    SCHEDULE_WORDS = [
        "schedule", "set up", "add", "create", "book", "plan"
    ]

    REMINDER_WORDS = [
        "remind", "reminder", "notify", "alert"
    ]

    MEETING_WORDS = [
        "meeting", "call", "event", "appointment", "session"
    ]

    TASK_WORDS = [
        "task", "workout", "gym", "exercise", "todo", "to do"
    ]

    TIME_WORDS = [
        "tomorrow", "today", "pm", "am", "at"
    ]

    # -----------------------------
    # COMPOSITE TASK + REMINDER + CALENDAR INTENT
    # -----------------------------
    if (
        any(w in text for w in SCHEDULE_WORDS)
        or any(w in text for w in REMINDER_WORDS)
    ):
        agents = []

        # Always treat as a task
        agents.append("TaskAgent")

        # If reminder intent exists
        if any(w in text for w in REMINDER_WORDS):
            agents.append("NotificationAgent")

        # If time/date semantics exist, attach calendar
        if (
            any(w in text for w in MEETING_WORDS)
            or any(w in text for w in TASK_WORDS)
            or any(w in text for w in TIME_WORDS)
        ):
            agents.append("CalendarAgent")

        # System-level agents (observability & feedback)
        agents.append("ReportAgent")
        agents.append("XPAgent")

        # Basic time defaults (safe, deterministic)
        start = datetime.utcnow() + timedelta(days=1)
        end = start + timedelta(hours=1)

        return {
            "plan_id": str(uuid.uuid4()),
            "intent": "task_with_reminder",
            "actions": [
                "create_task",
                "schedule_reminder",
                "create_calendar_event"
            ],
            "agents": agents,
            "params": {
                "raw_input": user_input,
                "title": "NeuroFlow Task / Event",
                "start": start.isoformat(),
                "end": end.isoformat()
            },
            "priority": "medium",
            "confidence": 0.9,
            "reasoning": "User requested a task with reminder and time-based execution",
            "requires_approval": True,
            "created_at": datetime.utcnow().isoformat()
        }

    # -----------------------------
    # FALLBACK (SAFE DEFAULT)
    # -----------------------------
    return {
        "plan_id": str(uuid.uuid4()),
        "intent": "unknown",
        "actions": [],
        "agents": ["ReportAgent"],
        "params": {
            "raw_input": user_input
        },
        "priority": "low",
        "confidence": 0.2,
        "reasoning": "Could not confidently map input to an executable workflow",
        "requires_approval": False,
        "created_at": datetime.utcnow().isoformat()
    }














