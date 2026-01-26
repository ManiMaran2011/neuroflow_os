import uuid
import json
from datetime import datetime
from backend.utils.llm import ask_llm


async def create_plan_with_llm(user_input: str) -> dict:
    prompt = f"""
You are an execution planner for an agentic AI OS.

Classify the user command into ONE of:
- one_time
- tracking
- recurring

Choose agents ONLY from:
- CalendarAgent
- MonitorAgent
- NotifyAgent
- XPAgent
- ReportAgent

Rules:
- Tracking goals (fitness, habits, learning) → tracking
- Tracking ALWAYS includes MonitorAgent
- Tracking reminders → NotifyAgent
- XP is awarded only via XPAgent
- CalendarAgent ONLY if user explicitly wants calendar visibility

Return STRICT JSON ONLY:

{{
  "execution_type": "one_time | tracking | recurring",
  "intent": string,
  "agents": string[],
  "schedule": {{
    "frequency": "daily | weekly | null",
    "time": "HH:MM" | null,
    "duration_days": number | null
  }},
  "params": object,
  "requires_approval": boolean
}}
"""

    response = await ask_llm(prompt + f"\nUser command: {user_input}")
    data = json.loads(response)

    return {
        "plan_id": str(uuid.uuid4()),
        "execution_type": data["execution_type"],
        "intent": data["intent"],
        "agents": data["agents"],
        "schedule": data.get("schedule"),
        "params": data.get("params", {}),
        "requires_approval": data.get("requires_approval", False),
        "created_at": datetime.utcnow().isoformat(),
    }


