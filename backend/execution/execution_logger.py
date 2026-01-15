import time
from backend.execution.execution import AgentLog


class ExecutionLogger:

    @staticmethod
    async def run_agent(agent, input_data, execution):
        log = AgentLog(
            agent_name=agent.name,
            input=input_data,
            output={},
            status="running"
        )

        execution.add_timeline(f"{agent.name} started")

        try:
            result = await agent.run(input_data)
            log.output = result
            log.status = "success"
            return log

        except Exception as e:
            log.status = "failed"
            log.error = str(e)
            raise

        finally:
            log.finished_at = time.time()
            execution.log_agent(log)
            execution.add_timeline(f"{agent.name} finished ({log.status})")
