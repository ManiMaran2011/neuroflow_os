import uuid

def create_plan(intent: dict):
    return {
        "plan_id": str(uuid.uuid4()),
        "intent": intent.get("intent"),
        "agents": intent.get("agents", []),
        "priority": intent.get("priority", "low"),
        "confidence": intent.get("confidence", 0.5),
        "reasoning": intent.get("reasoning", ""),
        "requires_approval": True
    }







