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
    tokens, cost = estimate_cost(
        plan.get("reasoning", plan.get("params", {}).get("raw_input", ""))
    )

    # ---------------- EXECUTION TYPE ----------------
    execution_type = plan.get("execution_type", "one_time")

    # ---------------- ACTIONS ----------------
    actions = plan.get("actions") or []

    # ---------------- AGENTS (SANITIZED) ----------------
    agents = plan.get("agents") or []

    # NEVER allow planner names as execution agents
    agents = [a for a in agents if a != "LLMPlanner"]

    if not agents:
        if execution_type == "tracking":
            agents = ["MonitorAgent", "NotifyAgent", "XPAgent", "ReportAgent"]
        else:
            agents = ["ReportAgent", "XPAgent"]

    # ---------------- PARAMS ----------------
    params = plan.get("params", {})
    params.setdefault("execution_type", execution_type)
    params.setdefault("schedule", plan.get("schedule"))
    params.setdefault("agent_results", {})
    params.setdefault("agent_errors", {})

    if "action" in plan:
        params["action"] = plan["action"]

    # ---------------- STATUS ----------------
    if execution_type == "tracking":
        status = "active"
        requires_approval = False
    else:
        requires_approval = plan.get("requires_approval", False)
        status = "awaiting_approval" if requires_approval else "created"

    # ---------------- EXECUTION ----------------
    execution = Execution(
        id=plan["plan_id"],
        user_email=user_email,
        intent=plan.get("intent", "agentic_execution"),
        actions=actions,
        agents=agents,
        params=params,
        requires_approval=requires_approval,
        status=status,
        estimated_tokens=tokens,
        estimated_cost=cost,
    )

    db.add(execution)
    db.commit()
    db.refresh(execution)

    db.add(
        ExecutionTimeline(
            execution_id=execution.id,
            message=f"Execution created (type={execution_type}, est cost=${cost})"
        )
    )
    db.commit()

    return execution


# ------------------------------------------------
# APPROVE EXECUTION (ONE-TIME ONLY)
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
        execution.xp_gained += xp_awarded
        db.commit()

        db.add(
            ExecutionTimeline(
                execution_id=execution.id,
                message=f"XP awarded: +{xp_awarded}"
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





