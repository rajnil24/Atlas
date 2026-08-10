from typing import Any

from backend.agent.execution_context import ExecutionContext
from backend.models.feedback import Feedback
from backend.models.plan import PlanStep
from backend.models.step_attempt import StepAttempt
from backend.services.llm import LLMClient

RECOVERY_PROMPT = """
You are the recovery component of an autonomous AI agent.

A tool attempted to execute a step, but the result requires revision.

Your job is to generate the corrected INPUT for the same tool.

You are NOT supposed to solve the user's original task directly.
You are supposed to fix the tool input so that the tool can try again.

Return ONLY valid JSON.

Required format:

{{
    "tool_input": {{
        ...
    }}
}}

Original step:
{step}

Previous attempt:
{attempt}

Feedback:
{feedback}
"""


class RecoveryManager:

    def __init__(self):
        self.llm = LLMClient()

    async def recover(
        self,
        step: PlanStep,
        attempt: StepAttempt,
        feedback: Feedback,
    ) -> dict[str, Any] | None:

        prompt = RECOVERY_PROMPT.format(
            step=step.model_dump(),
            attempt=attempt.model_dump(),
            feedback=feedback.model_dump(),
        )

        response = await self.llm.generate(prompt)
        print(response)
        recovery_input = self._parse_response(response)

        return recovery_input

    def _parse_response(
        self,
        response: str,
    ) -> dict[str, Any] | None:

        ...