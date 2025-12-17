async def classify_intent(user_input: str) -> str:
    text = user_input.lower()

    if "task" in text or "todo" in text:
        return "task"
    if "calendar" in text or "schedule" in text:
        return "calendar"
    if "research" in text or "search" in text:
        return "research"
    if "contact" in text:
        return "contact"
    if "notify" in text or "remind" in text:
        return "notification"
    if "energy" in text:
        return "energy"
    if "report" in text:
        return "report"

    return "xp"
