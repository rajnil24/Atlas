from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field
from backend.models.step_attempt import StepAttempt


class StepStatus(str, Enum):

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PlanStep:
    
    step_id : str
    tool_name: str
    tool_input: dict[str, Any] = Field(default_factory=dict)

    status: StepStatus = StepStatus.PENDING

    depends_on : list[str] = Field(default_factory=list)

    output: Optional[Any] = None
    error: Optional[str] = None

    retries : int = 0 
    max_retries : int = 2 

    attempts : list[StepAttempt] = Field(default_factory = list)
    



@dataclass
class Plan(BaseModel):
    steps: list[PlanStep] = field(default_factory=list)
    plan_response : str = ""