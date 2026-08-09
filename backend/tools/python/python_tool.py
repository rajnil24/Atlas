from backend.tools.python.models import PythonInput , PythonOutput
from execution.docker_executor import DockerExecutor
from backend.tools.base_tools import BaseTool, ToolResult
from pathlib import Path
from execution.execution_status import ExecutionStatus
import tempfile

class PythonTool(BaseTool) :
    tool_name = "python"
    input_schema = PythonInput
    tool_description = """
Executes arbitrary Python code inside a secure Docker sandbox.
-Use this tool whenever solving a task requires computation,
data processing, file generation, scripting or Python libraries.
-

Capabilities:

- Executes Python 3.13 code.
- Captures stdout and stderr.
- Reports execution status.
- Enforces CPU, memory, timeout and process limits.
- Runs without internet access.
- Executes as a non-root user.
- Returns any files created inside the workspace.
"""

    def __init__(self) :
        self.executor = DockerExecutor()

    async def run(self, input_data: PythonInput) -> ToolResult:

        with tempfile.TemporaryDirectory(prefix="atlas_") as temp_dir:

            workspace = Path(temp_dir)

            code_file = workspace / "generated_code.py"

            code_file.write_text(input_data.code)

            execution_result = self.executor.execute(workspace)

            python_output = PythonOutput(

                status=execution_result.status,

                stdout=execution_result.stdout,

                stderr=execution_result.stderr,

                execution_time=execution_result.execution_time,

                exit_code=execution_result.exit_code,

                files_created=[]

            )

            return ToolResult(

                success=True,

                output=python_output

            )

