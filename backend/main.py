from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .parent_agent import parent_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def ask(data: dict):
    user_input = data.get("input", "")
    result = await parent_agent.handle(user_input)
    return {"response": result}
