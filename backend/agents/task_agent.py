import os
import json
from base_agent import BaseAgent


class TaskAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="TaskAgent",
            db_path="backend/database/tasks_db.json"
        )

    async def run(self, user_input: str):
        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # Initialize DB file if missing
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w") as f:
                json.dump([], f)

        # Load existing tasks
        with open(self.db_path, "r") as f:
            tasks = json.load(f)

        # Add new task
        new_task = {"task": user_input}
        tasks.append(new_task)

        # Save back to DB
        with open(self.db_path, "w") as f:
            json.dump(tasks, f, indent=2)

        return {
            "agent": self.name,
            "status": "success",
            "message": "Task added",
            "data": new_task
        }



