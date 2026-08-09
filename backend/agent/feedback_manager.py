from backend.models.feedback import Feedback, FeedbackVerdict
from backend.tools.base_tools import ToolResult , BaseTool
from backend.models.plan import PlanStep

class FeedbackManager:

    async def evaluate(
        self,
        step: PlanStep,
        tool: BaseTool,
        validated_input,
        result: ToolResult,
    ) -> Feedback:

        # Tool execution itself failed.
        if not result.success:
            return Feedback(
                verdict=FeedbackVerdict.FAIL,
                reason=result.error or "Tool execution failed.",
                retryable=False,
            )

        # Ask the tool whether it has an objective validator.
        validation = await tool.validate(
            validated_input,
            result,
        )

        # No deterministic validator.
        if validation is None:
            # Critic LLM will be added here later.
            return Feedback(
                verdict=FeedbackVerdict.PASS,
                reason="Tool executed successfully; no deterministic validator available.",
                retryable=False,
            )

        return validation