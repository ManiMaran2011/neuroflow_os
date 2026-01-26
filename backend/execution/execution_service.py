from sqlalchemy.orm import Session
from backend.db.models import Execution, ExecutionTimeline, User
from backend.parent_agent import ParentAgent


# -------------------------
# SIMPLE COST ESTIMATION
# -------------------------
def estimate_cost(text: str):
    estimated_tokens = max(100, len(text.split()) * 10)
    estimated_cost = round((estimated_tokens / 1000) * 0.01, 4)
    return estimated_tokens, estimated_cost


# ------------------------------------------------
# CREATE EXECUTION
# ------------------------------------------------
def create_execution(db: Session, user_email: str, plan: dict) -> Execution:
    # ---------------- USER ----------------
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        user = User(email=user_email)
        db.add(user)
        db.commit()

    # ---------------- COST ----------------
    tokens, cost = estimate_cost(plan.get("reasoning", plan.get("params", {}).get("raw_input", "")))

    # ---------------- NORMALIZE PLAN ----------------

    # ACTIONS
    actions = plan.get("actions")
    if not actions:
        execution_channel = plan.get("execution_channel")
        actions = [execution_channel] if execution_channel else []

    # AGENTS
    agents = plan.get("agents")
    if not agents:
        channel = plan.get("execution_channel")
        if channel == "calendar":
            agents = ["CalendarAgent", "NotificationAgent", "ReportAgent", "XPAgent"]
        elif channel == "email":
            agents = ["EmailAgent", "ReportAgent", "XPAgent"]
        else:
            agents = ["ReportAgent", "XPAgent"]

    # PARAMS
    params = plan.get("params", {})
    if "action" in plan:
        params["action"] = plan["action"]

    requires_approval = plan.get("requires_approval", True)

    # ---------------- EXECUTION ----------------
    execution = Execution(
        id=plan["plan_id"],
        user_email=user_email,
        intent=plan.get("intent", "agentic_execution"),
        actions=actions,
        agents=agents,
        params=params,
        requires_approval=requires_approval,
        status="awaiting_approval",
        estimated_tokens=tokens,
        estimated_cost=cost
    )

    db.add(execution)
    db.commit()
    db.refresh(execution)

    # ---------------- TIMELINE ----------------
    db.add(
        ExecutionTimeline(
            execution_id=execution.id,
            message=f"Execution created (Est. cost: ${cost})"
        )
    )
    db.commit()

    return execution


# ------------------------------------------------
# APPROVE EXECUTION
# ------------------------------------------------
async def approve_execution(db: Session, execution: Execution):
    if execution.status != "awaiting_approval":
        raise ValueError(f"Execution is in '{execution.status}' state")

    execution.status = "executing"
    db.commit()

    db.add(
        ExecutionTimeline(
            execution_id=execution.id,
            message="Execution approved by user"
        )
    )
    db.commit()

    parent_agent = ParentAgent()

    result = await parent_agent.handle(
        db=db,
        execution=execution,
        execution_plan={
            "intent": execution.intent,
            "actions": execution.actions,
            "agents": execution.agents,
            "params": execution.params
        },
        user_input=execution.params.get("raw_input")
    )

    execution.status = "executed"
    db.commit()

    # ---------------- XP ----------------
    user = db.query(User).filter(User.email == execution.user_email).first()
    xp_awarded = 15

    if user:
        user.xp += xp_awarded
        db.commit()

        db.add(
            ExecutionTimeline(
                execution_id=execution.id,
                message=f"XP awarded: +{xp_awarded} (Total XP: {user.xp})"
            )
        )
        db.commit()

    return {
        "status": "executed",
        "execution_id": execution.id,
        "result": result,
        "xp_awarded": xp_awarded,
        "total_xp": user.xp if user else None,
        "estimated_tokens": execution.estimated_tokens,
        "estimated_cost": execution.estimated_cost
    }




