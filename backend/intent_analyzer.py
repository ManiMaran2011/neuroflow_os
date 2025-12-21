import uuid

class IntentAnalyzer:
    async def analyze(self, user_input: str):
        text = user_input.lower()

        act_keywords = [
            "add",
            "create",
            "set",
            "remind",
            "schedule",
            "save",
            "delete",
            "update",
            "do it again"
        ]

        mode = "ACT" if any(k in text for k in act_keywords) else "THINK"

        if "do it again" in text:
            intent = "replay"
        elif "task" in text and "remind" in text:
            intent = "task_with_reminder"
        elif "task" in text:
            intent = "task"
        elif "remind" in text:
            intent = "reminder"
        elif "calendar" in text:
            intent = "calendar"
        else:
            intent = "informational"

        return {
            "id": str(uuid.uuid4()),
            "intent": intent,
            "mode": mode
        }



