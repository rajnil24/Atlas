from typing import Any
import json
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
        print("inside recovery manager")
        prompt = RECOVERY_PROMPT.format(
            step=step.model_dump(),
            attempt=attempt.model_dump(),
            feedback=feedback.model_dump(),
        )
        print(prompt)
        response = await self.llm.generate(prompt)
        print("response is" , response)
        recovery_input = self._parse_response(response)
        print("recovery input is" , recovery_input)

        return recovery_input

    def _parse_response(
    self,
    response: str,
    ) -> dict[str, Any] | None:
        print("inside parse response")
        if not response:
            return None
 
        cleaned = response.strip()

        if cleaned.startswith("```"):

            lines = cleaned.splitlines()

            lines = lines[1:]

            if lines and lines[-1].strip() == "```":
               lines.pop()

            cleaned = "\n".join(lines).strip()

        try:
            data = json.loads(cleaned)

        except json.JSONDecodeError:
            return None

        if not isinstance(data, dict):
            return None
        
        tool_input = data.get("tool_input")
        print(tool_input)
        print(type(tool_input))
        if tool_input is None:
            return None

        if not isinstance(tool_input, dict):
            return None

        return tool_input
        

        

