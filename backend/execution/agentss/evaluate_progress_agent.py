import json
from datetime import datetime
from typing import Dict, List, Optional

from backend.utils.llm import ask_llm


class EvaluateProgressAgent:
    """
    Uses an LLM to evaluate whether a user is progressing
    and recommends next actions if needed.
    """

    name = "EvaluateProgressAgent"

    async def run(
        self,
        plan: Dict,
        execution_history: List[Dict],
        now: Optional[datetime] = None,
    ) -> Dict:
        now = now or datetime.utcnow()

        prompt = f"""
You are an autonomous progress evaluator for an agentic AI system.

Your job:
- Decide if the user is making progress
- If not, suggest ONE corrective action

Return STRICT JSON ONLY.
NO explanations.
NO markdown.

Schema:
{{
  "action_needed": boolean,
  "execution_channel": "calendar" | "slack" | "email" | null,
  "reason": string,
  "suggested_action": string | null
}}

Guidelines:
- If user is on track → action_needed = false
- If user missed multiple actions → suggest gentle nudge
- Prefer Slack for check-ins
- Prefer Calendar for scheduling
- Emails ALWAYS require approval (but you don't handle approval here)
"""

        context = {
            "current_time": now.isoformat(),
            "plan": plan,
            "execution_history": execution_history,
        }

        try:
            raw = await ask_llm(
                prompt + "\n\nContext:\n" + json.dumps(context, indent=2)
            )

            result = json.loads(raw)

            # 🔒 Hard safety validation
            if "action_needed" not in result:
                raise ValueError("Missing action_needed")

            return {
                "agent": self.name,
                "action_needed": result["action_needed"],
                "execution_channel": result.get("execution_channel"),
                "reason": result.get("reason", ""),
                "suggested_action": result.get("suggested_action"),
            }

        except Exception:
            # 🔁 Fail-safe: do nothing if LLM fails
            return {
                "agent": self.name,
                "action_needed": False,
                "execution_channel": None,
                "reason": "Evaluation failed — defaulting to no action",
                "suggested_action": None,
            }
