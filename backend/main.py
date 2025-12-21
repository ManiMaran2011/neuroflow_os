from fastapi import FastAPI
from pydantic import BaseModel
from parent_agent import ParentAgent
from utils.router import classify_intent
from planner import create_plan

app = FastAPI()
parent_agent = ParentAgent()

LAST_EXECUTION_PLAN = None

class AskRequest(BaseModel):
    user_input: str
    approved: bool | None = False
    execution_plan: dict | None = None

@app.post("/ask")
async def ask(req: AskRequest):
    global LAST_EXECUTION_PLAN

    if not req.approved:
        text = req.user_input.lower().strip()

        if text == "do it again" and LAST_EXECUTION_PLAN:
            return {
                "status": "awaiting_approval",
                "execution_plan": LAST_EXECUTION_PLAN,
                "timeline": [
                    "Previous execution recalled from memory",
                    "Execution paused for approval"
                ]
            }

        intent = await classify_intent(req.user_input)

        if intent["mode"] == "THINK":
            result = await parent_agent.handle(req.user_input)
            return {
                "status": "think",
                "answer": result["results"]["ResearchAgent"],
                "timeline": [
                    "Intent analyzed",
                    "Reasoning completed"
                ]
            }

        plan = create_plan(intent)
        LAST_EXECUTION_PLAN = plan

        return {
            "status": "awaiting_approval",
            "execution_plan": plan,
            "timeline": [
                "Intent analyzed",
                "Execution plan created",
                "Execution paused for approval"
            ]
        }

    result = await parent_agent.handle(
        req.user_input,
        req.execution_plan
    )

    LAST_EXECUTION_PLAN = req.execution_plan

    return {
        "status": "executed",
        "execution_plan": req.execution_plan,
        "timeline": [
            "Execution approved",
            "Action agents executed",
            "XP rewarded"
        ],
        "results": result["results"]
    }






















