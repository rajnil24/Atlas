from backend.models.feedback import Feedback
from backend.tools.base_tools import ToolResult , BaseTool
from backend.models.plan import PlanStep
from backend.services.llm import LLMClient
import json 

class FeedbackManager:

    async def evaluate(
    self,
    step: PlanStep,
    tool: BaseTool,
    validated_input,
    result: ToolResult,
) -> Feedback:

    # ------------------------------------------------
    # 1. Deterministic validation
    # ------------------------------------------------

        validation = await tool.validate(
            validated_input,
            result,
            )

    # ------------------------------------------------
    # 2. Validator exists and gives a verdict
    # ------------------------------------------------

        if validation is not None:
            return validation

    # ------------------------------------------------
    # 3. No deterministic validator
    # ------------------------------------------------

        return await self._critic_evaluate(
            step=step,
            validated_input=validated_input,
            result=result,
            )

    async def _critic_evaluate(
    self,
    step: PlanStep,
    validated_input,
    result: ToolResult,
) -> Feedback:

        previous_attempts = step.attempt_history

        llm = LLMClient()

        CRITIC_PROMPT = """
You are the feedback evaluator of an autonomous AI agent.

Your job is to determine whether the CURRENT tool execution
successfully satisfies the intent of the logical step.

You have:

1. Original step
2. Current attempt input
3. Current tool result
4. Previous attempts and feedback

Previous feedback is provided so that you can determine whether
the current attempt actually improved the situation.

Possible verdicts:

PASS
- The current result satisfies the step.

NEEDS_REVISION
- The result does not satisfy the step yet,
- but the problem appears recoverable by changing the input.
- Another attempt should be made.

FAIL
- The step cannot reasonably be completed through another retry,
- or the failure requires human intervention.

Return ONLY JSON:

{{
    "verdict": "pass | needs_revision | fail",
    "reason": "...",
    "retryable": true | false
}}

ORIGINAL STEP:
{step}

ORIGINAL INPUT:
{original_input}

CURRENT INPUT:
{current_input}

CURRENT RESULT:
{current_result}

PREVIOUS ATTEMPTS:
{previous_attempts}

The verdict MUST be exactly one of:

"pass"
"needs_revision"
"fail"

Return lowercase values only.

Never return:
"PASS"
"Pass"
"NEEDS_REVISION"
"Fail"
"""

        prompt = CRITIC_PROMPT.format(
        step=step.model_dump(),
        original_input=step.tool_input,
        current_input=validated_input,
        current_result=result.model_dump(),
        previous_attempts=previous_attempts,
        )
        print("inside feedback_mamager.py line 129")
        response = await llm.generate(prompt)
        print("response is ->>" , response)
        return self._parse_feedback(response)

    def _parse_feedback(self, response: str) -> Feedback:

        cleaned = response.strip()

        if cleaned.startswith("```"):

            lines = cleaned.splitlines()

            if lines[0].startswith("```"):

               lines = lines[1:]

            if lines and lines[-1].strip() == "```":

               lines = lines[:-1]

            cleaned = "\n".join(lines)

        data = json.loads(cleaned)
        print("inside feedback_mamager.py line 153")
        print(data)
        return Feedback.model_validate(data)