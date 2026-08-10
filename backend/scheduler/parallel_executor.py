import asyncio
from backend.agent.execution_context import ExecutionContext
from backend.scheduler.scheduler import Scheduler
from backend.models.step_attempt import StepAttempt
from backend.models.plan import PlanStep, StepStatus , Plan
from backend.tools.registry import ToolRegistry
from backend.tools.base_tools import ToolResult 
from backend.models.feedback import FeedbackVerdict , Feedback
from backend.agent.recovery import RecoveryManager
from backend.agent.feedback_manager import FeedbackManager

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

            attempt_number = len(step.attempts) + 1

            attempt_input = self._get_attempt_input(step)

            resolved_input = context.resolve(attempt_input)

            try:

                tool = self.registry.get_tool(step.tool_name)
                validated_input = tool.input_schema(**resolved_input)

                result = await asyncio.wait_for(
                    tool.run(validated_input),
                    timeout=self.step_timeout,
                )
  
            except Exception as e:

                result = ToolResult(
                success=False,
                output=None,
                error=str(e),
            )

            feedback_manager = FeedbackManager()

            tool = self.registry.get_tool(step.tool_name)

            feedback = await feedback_manager.evaluate(
                step=step,
                tool=tool,
                validated_input=validated_input,
                result=result,
            )

            attempt = StepAttempt(
                attempt_number = attempt_number , 
                tool_name = step.tool_name ,
                tool_input = resolved_input ,
                result = result ,
                feedback = feedback ,
            )
            print("parallel_executor.py line 114 " )
            print(attempt)

            step.attempt_history.append({
                "attempt_number" : attempt_number , 
                "tool_input" : attempt_input ,
                "result" : result.model_dump() ,
                "feedback" : feedback.model_dump() ,
            })

            step.attempts.append(attempt)
            print("feedback verdict is -> " , feedback.verdict)
            if feedback.verdict == FeedbackVerdict.PASS :
                step.output = result.output 
                step.status = StepStatus.SUCCESS 

                context.set_result(
                step.step_id,
                result.output,
                )
                scheduler.mark_completed(step.step_id)
            
            elif feedback.verdict == FeedbackVerdict.NEEDS_REVISION :
                await self._handle_revision(
                step,
                feedback,
                scheduler,
                )

            elif feedback.verdict == FeedbackVerdict.FAIL :

                step.status = StepStatus.FAILED
                step.error = feedback.reason
                scheduler.mark_failed(step.step_id)
            
    async def _handle_revision(
        self,
        step: PlanStep,
        feedback: Feedback,
        scheduler: Scheduler,
    ):
            print("inside handle rev")
            if step.retries >= step.max_retries:
               step.status = StepStatus.FAILED
               step.error = (
               f"Maximum retries exceeded. "
               f"Last feedback: {feedback.reason}"
               )
               scheduler.mark_failed(step.step_id)
               print("max retries done")
               return
            
            last_attempt = step.attempts[-1]

            recovery_manager = RecoveryManager()

            recovery_input = await recovery_manager.recover(
            step=step,
            attempt=last_attempt,
            feedback=feedback,
            )

            if recovery_input is None:
               print("recovery is none *********")
               step.status = StepStatus.FAILED
               step.error = (
               "Revision requested but recovery "
               "could not produce new input."
               )
               scheduler.mark_failed(step.step_id)
               return

            last_attempt.recovery_input = recovery_input
            step.retries += 1
            print(step.retries)
            step.status = StepStatus.PENDING
            scheduler.dispatched.discard(step.step_id)

    def _get_attempt_input(self, step: PlanStep) -> dict:
        """
        Return the input that should be used for the next attempt.
        """

        if not step.attempts:
            # First attempt
            return step.tool_input
        
        # Retry input will eventually come from RecoveryManager.
        last_attempt = step.attempts[-1]

        if last_attempt.recovery_input is None:
            raise RuntimeError(
               f"No recovery input available for {step.step_id}"
            )
        
        return last_attempt.recovery_input     

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