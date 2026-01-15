from datetime import datetime
import uuid

class Execution:
    def __init__(self, user_id: str):
        self.execution_id = str(uuid.uuid4())
        self.user_id = user_id
        self.plan = None
        self.timeline = []
        self.created_at = datetime.utcnow().isoformat()

        self.add_timeline("Execution created")

    def add_timeline(self, message: str):
        timestamp = datetime.utcnow().isoformat()
        self.timeline.append(f"{timestamp} — {message}")







