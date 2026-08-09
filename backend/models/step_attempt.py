from typing import Any
from pydantic import BaseModel, Field

from backend.models.feedback import Feedback
from backend.tools.base_tools import ToolResult


class StepAttempt(BaseModel):
    attempt_number: int
    tool_name : str 
    tool_input: dict[str, Any]
    result: ToolResult
    feedback: Feedback | None = None
    recovery_input: dict[str, Any] | None = None