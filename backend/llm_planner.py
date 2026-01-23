import uuid
import json
from datetime import datetime

from backend.utils.llm import ask_llm


async def create_plan_with_llm(user_input: str) -> dict:
    prompt = f"""
You are an execution planner for an agentic AI system.

Given a user command, decide:
1. execution_channel: calendar | slack | email
2. whether approval is required
3. structured action details

Return STRICT JSON ONLY in this format:

{{
  "execution_channel": "calendar | slack | email",
  "requires_approval": boolean,
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
- Calendar events under 1 hour → no approval
- Emails → always require approval
"""

    response = await ask_llm(prompt + f"\nUser command: {user_input}")

    data = json.loads(response)

    return {
        "plan_id": str(uuid.uuid4()),
        "intent": "llm_routed_execution",
        "execution_channel": data["execution_channel"],
        "requires_approval": data["requires_approval"],
        "action": data["action"],
        "confidence": 0.95,
        "created_at": datetime.utcnow().isoformat(),
    }
