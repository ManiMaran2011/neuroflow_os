import json
from ..base_agent import BaseAgent

class TaskAgent(BaseAgent):
    def __init__(self):
        super().__init__("tasks_db.json", "TaskAgent")

    async def run(self, instruction: str):
        with open(self.db_path, "r") as f:
            data = json.load(f)

        task_id = str(len(data) + 1)
        data[task_id] = {"task": instruction}

        with open(self.db_path, "w") as f:
            json.dump(data, f, indent=2)

        return f"Task added: {instruction}"

