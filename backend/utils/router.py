# backend/utils/router.py

async def classify_intent(user_input: str) -> dict:
    """
    Lightweight intent classifier (MVP).
    """

    text = user_input.lower()

    # ---- Scheduling intent ----
    if "schedule" in text or "meeting" in text or "calendar" in text:
        return {
            "mode": "ACT",
            "intent": "schedule_meeting",
            "params": {},
            "confidence": 0.9,
            "priority": "medium",
            "reasoning": "User wants to schedule a meeting"
        }

    # ---- Default THINK mode ----
    return {
        "mode": "THINK",
        "intent": "general_query",
        "params": {},
        "confidence": 0.3,
        "priority": "low",
        "reasoning": "No actionable intent detected"
    }

