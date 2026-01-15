from typing import Any, Dict, List
from datetime import datetime


class ExecutionRecord:
    def __init__(
        self,
        execution_id: str,
        user_id: str,
        intent: str,
        plan: Dict[str, Any],
        status: str,
        results: Dict[str, Any] | None = None,
        timeline: List[str] | None = None,
        created_at: str | None = None,
    ):
        self.execution_id = execution_id
        self.user_id = user_id
        self.intent = intent
        self.plan = plan
        self.status = status
        self.results = results or {}
        self.timeline = timeline or []
        self.created_at = created_at or datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "user_id": self.user_id,
            "intent": self.intent,
            "plan": self.plan,
            "status": self.status,
            "results": self.results,
            "timeline": self.timeline,
            "created_at": self.created_at,
        }
