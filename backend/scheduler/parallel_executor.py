import asyncio

from backend.agent.execution_context import ExecutionContext
from backend.scheduler.scheduler import Scheduler
from backend.models.plan import Plan
from backend.models.plan import PlanStep, StepStatus
from backend.tools.registry import ToolRegistry


class ParallelExecutor:

    def __init__(
        self,
        registry: ToolRegistry,
        max_concurrency: int = 5,
        step_timeout: float = 20.0,
    ):
        self.registry = registry
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.step_timeout = step_timeout

    async def execute_plan(self, plan: Plan) -> ExecutionContext:

        context = ExecutionContext()
        scheduler = Scheduler(plan)

        while not scheduler.is_done():

            ready_steps = scheduler.get_ready_steps()

            if not ready_steps:

                # No new work, but some tasks are still running.
                if scheduler.dispatched:
                    await asyncio.sleep(0.05)
                    continue

                # Nothing running and nothing ready.
                # Planner probably produced an invalid dependency graph.
                self._fail_remaining(
                    scheduler,
                    "Unresolvable dependency (missing dependency or circular dependency)"
                )
                break

            for step in ready_steps:
                scheduler.mark_dispatched(step.step_id)

            tasks = [
                self._run_step(step, context, scheduler)
                for step in ready_steps
            ]

            await asyncio.gather(*tasks)

        return context

    async def _run_step(
        self,
        step: PlanStep,
        context: ExecutionContext,
        scheduler: Scheduler,
    ):

        async with self.semaphore:

            step.status = StepStatus.RUNNING

            try:

                tool = self.registry.get(step.tool_name)

                resolved_input = context.resolve(step.tool_input)

                validated_input = tool.input_schema(**resolved_input)

                result = await asyncio.wait_for(
                    tool.run(validated_input),
                    timeout=self.step_timeout,
                )

                if not result.success:
                    raise RuntimeError(result.error)

                step.output = result.output
                step.status = StepStatus.SUCCESS

                await context.set_result(
                    step.step_id,
                    result.output,
                )

                scheduler.mark_completed(step.step_id)

            except Exception as e:

                step.status = StepStatus.FAILED
                step.error = str(e)

                scheduler.mark_failed(step.step_id)

    def _fail_remaining(
        self,
        scheduler: Scheduler,
        reason: str,
    ):

        for step_id in scheduler.graph.all_step_ids():

            if (
                step_id not in scheduler.completed
                and step_id not in scheduler.failed
                and step_id not in scheduler.blocked
            ):

                step = scheduler.graph.get_step(step_id)

                step.status = StepStatus.FAILED
                step.error = reason

                scheduler.failed.add(step_id)