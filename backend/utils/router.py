async def classify_intent(user_input: str):
    text = user_input.lower()

    action_keywords = [
        "add",
        "create",
        "remind",
        "schedule",
        "set",
        "notify",
        "book",
        "do it again"
    ]

    think_keywords = [
        "what is",
        "explain",
        "define",
        "how does",
        "tell me about"
    ]

    if any(k in text for k in action_keywords):
        agents = []

        if "task" in text or "add" in text:
            agents.append("TaskAgent")

        if "remind" in text or "notify" in text:
            agents.append("NotificationAgent")

        if not agents:
            agents.append("TaskAgent")

        return {
            "mode": "ACT",
            "intent": "task_with_reminder",
            "agents": agents,
            "priority": "high",
            "confidence": 0.9
        }

    if any(k in text for k in think_keywords):
        return {
            "mode": "THINK",
            "intent": "informational",
            "agents": ["ResearchAgent"],
            "confidence": 0.9
        }

    return {
        "mode": "THINK",
        "intent": "unknown",
        "agents": ["ResearchAgent"],
        "confidence": 0.5
    }

