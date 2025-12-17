import json
import os


class BaseAgent:
    def __init__(self, name: str, db_path: str | None = None):
        self.name = name
        self.db_path = db_path

        if self.db_path:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            if not os.path.exists(self.db_path):
                with open(self.db_path, "w") as f:
                    json.dump([], f)

    async def run(self, user_input: str):
        raise NotImplementedError("Agent must implement run()")
