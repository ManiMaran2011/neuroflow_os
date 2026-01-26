from backend.agent_registry import get_agent_instances
from backend.db.models import ExecutionTimeline
import traceback


class ParentAgent:
    async def handle(self, db, execution, execution_plan, user_input):
        # ---------------- INIT RUNTIME STATE ----------------
        if execution.params is None:
            execution.params = {}

        # 🔑 CRITICAL FIX
        execution.params.setdefault("agent_results", {})
        execution.params.setdefault("agent_errors", {})

        db.commit()

        db.add(
            ExecutionTimeline(
                execution_id=execution.id,
                message="ParentAgent started execution"
            )
        )
        db.commit()

        agents = get_agent_instances(execution_plan.get("agents", []))

        for agent in agents:
            agent_name = agent.__class__.__name__

            db.add(
                ExecutionTimeline(
                    execution_id=execution.id,
                    message=f"{agent_name} execution started"
                )
            )
            db.commit()

            try:
                result = await agent.run(
                    user_input=user_input,
                    params=execution_plan.get("params", {})
                )

                # ✅ STORE RESULT
                execution.params["agent_results"][agent_name] = result
                db.commit()

                db.add(
                    ExecutionTimeline(
                        execution_id=execution.id,
                        message=f"{agent_name} execution completed"
                    )
                )
                db.commit()

            except Exception as e:
                error_result = {
                    "status": "error",
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }

                # ✅ STORE ERROR
                execution.params["agent_errors"][agent_name] = error_result
                db.commit()

                db.add(
                    ExecutionTimeline(
                        execution_id=execution.id,
                        message=f"{agent_name} execution failed"
                    )
                )
                db.commit()

        return {
            "status": "executed",
            "results": execution.params["agent_results"],
            "errors": execution.params["agent_errors"]
        }


























