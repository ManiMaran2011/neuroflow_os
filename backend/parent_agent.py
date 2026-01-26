from backend.agent_registry import get_agent_instances
from backend.db.models import ExecutionTimeline
import traceback


class ParentAgent:
    async def handle(self, db, execution, execution_plan, user_input):
        # Ensure container exists
        if not execution.params:
            execution.params = {}

        execution.params.setdefault("agent_results", {})

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
                message=f"{agent_name} started"
            ))
            db.commit()

            try:
                result = await agent.run(
                    user_input=user_input,
                    params=execution_plan.get("params", {})
                )

                # 🔑 Enforce contract
                if not isinstance(result, dict):
                    raise ValueError("Agent did not return dict")

                results[agent_name] = result

                # 🔥 Persist agent output
                execution.params["agent_results"][agent_name] = result
                db.commit()

                # 🔥 Human-readable timeline
                summary = result.get("summary")
                if summary:
                    db.add(ExecutionTimeline(
                        execution_id=execution.id,
                        message=f"{agent_name}: {summary}"
                    ))
                    db.commit()

            except Exception as e:
                error_result = {
                    "status": "error",
                    "effect": "agent_failed",
                    "summary": str(e),
                    "traceback": traceback.format_exc()
                }

                execution.params["agent_results"][agent_name] = error_result
                db.commit()

                db.add(ExecutionTimeline(
                    execution_id=execution.id,
                    message=f"{agent_name} failed: {str(e)}"
                ))
                db.commit()

        execution.status = "executed"
        db.commit()

        return {
            "status": "executed",
            "results": results
        }

























