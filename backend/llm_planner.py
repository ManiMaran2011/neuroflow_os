import uuid
import json
from datetime import datetime

from backend.utils.llm import ask_llm


async def create_plan_with_llm(user_input: str) -> dict:
    """
    LLM-based execution planner.

    IMPORTANT:
    - LLM decides WHAT to do (channel + action)
    - SYSTEM decides SAFETY (approval required)
    """

    prompt = f"""
You are an execution planner for an agentic AI system.

Given a user command, decide:
1. execution_channel: calendar | slack | email
2. structured action details

Return STRICT JSON ONLY in this format:

{{
  "execution_channel": "calendar | slack | email",
  "action": {{
    "summary": string,
    "description": string,
    "start_time": ISO8601 or null,
    "end_time": ISO8601 or null
  }}
}}

Rules:
- Meetings, reminders, scheduling → calendar
- Internal notifications → slack
- External communication → email
- Be precise with times if mentioned
- Do NOT include explanations
"""

    response = await ask_llm(prompt + f"\nUser command: {user_input}")

    data = json.loads(response)

    # ----------------------------
    # 🔐 SYSTEM SAFETY POLICY
    # ----------------------------
    # Any real-world side effect MUST be approved
    requires_approval = True

    return {
        "plan_id": str(uuid.uuid4()),
        "intent": "llm_routed_execution",
        "execution_channel": data["execution_channel"],
        "actions": [data["execution_channel"]],
        "agents": [
            "CalendarAgent" if data["execution_channel"] == "calendar" else
            "EmailAgent" if data["execution_channel"] == "email" else
            "NotificationAgent"
        ],
        "params": {
            "action": data["action"],
            "raw_input": user_input
        },
        "requires_approval": requires_approval,
        "confidence": 0.95,
        "created_at": datetime.utcnow().isoformat(),
    }

