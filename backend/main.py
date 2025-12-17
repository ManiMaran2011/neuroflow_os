from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class AskRequest(BaseModel):
    user_input: str

@app.post("/ask")
async def ask(req: AskRequest):
    from parent_agent import ParentAgent
    parent_agent = ParentAgent()
    result = await parent_agent.handle(req.user_input)
    return {"response": result}
