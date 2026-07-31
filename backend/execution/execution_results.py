from dataclasses import dataclass
from backend.execution.execution_status import ExecutionStatus
@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    status : ExecutionStatus
    exit_code: int
    timed_out: bool = False
    execution_time: float = 0.0
    