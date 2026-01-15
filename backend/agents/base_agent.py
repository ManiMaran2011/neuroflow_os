class BaseAgent:
    name = "BaseAgent"

    async def run(self, user_input: str, params: dict) -> dict:
        raise NotImplementedError("Agents must implement run()")


