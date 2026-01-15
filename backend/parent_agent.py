from backend.agent_registry import get_agent_instances
from backend.db.models import ExecutionTimeline
import traceback


class ParentAgent:
    async def handle(self, db, execution, execution_plan, user_input):
        db.add(ExecutionTimeline(
            execution_id=execution.id,
            message="ParentAgent started execution"
        ))
        db.commit()

        agents = get_agent_instances(execution_plan.get("agents", []))
        results = {}

        for agent in agents:
            agent_name = agent.__class__.__name__

            db.add(ExecutionTimeline(
                execution_id=execution.id,
                message=f"{agent_name} execution started"
            ))
            db.commit()

            try:
                result = await agent.run(
                    user_input=user_input,
                    params=execution_plan.get("params", {})
                )
            except Exception as e:
                result = {
                    "status": "error",
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }

            results[agent_name] = result

            db.add(ExecutionTimeline(
                execution_id=execution.id,
                message=f"{agent_name} execution completed"
            ))
            db.commit()

        execution.status = "executed"
        db.commit()

        return {
            "status": "executed",
            "results": results
        }
























