from pydantic import BaseModel
from backend.execution.execution_status import ExecutionStatus

class PythonInput(BaseModel):

    code: str

class PythonOutput(BaseModel):

    status: ExecutionStatus
    stdout: str
    stderr: str
    execution_time: float
    exit_code: int
    files_created: list[str] = []