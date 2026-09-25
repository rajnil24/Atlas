import asyncio
from pydantic import BaseModel
from backend.execution.docker_executor import DockerExecutor
from backend.execution.execution_status import ExecutionStatus
from backend.execution.temp_workspace import TempWorkspace
from backend.tools.base_tools import BaseTool , ToolResult

class CodeExecutionInput(BaseModel):
    code: str
    language: str = "python"


class CodeExecutionTool(BaseTool):

    tool_name = "code_executor"

    tool_description = """
    Executes Python code inside an isolated temporary Docker sandbox.
    Use this tool when Python code needs to be tested or executed.
    The code must be provided in the `code` field.
    """

    input_schema = CodeExecutionInput

    def __init__(self):

        self.executor = DockerExecutor(
            timeout=10
        )

    async def run(
        self,
        input_data: CodeExecutionInput,
    ) -> ToolResult:

        if input_data.language.lower() != "python":

            return ToolResult(
                success=False,
                output=None,
                error=(
                    f"Unsupported language: "
                    f"{input_data.language}"
                ),
            )

        workspace = TempWorkspace()



        try:

            
            workspace_path = workspace.create()

            print("code_execution_tool 56")

            workspace.write_code(
                input_data.code
            )

            result = await asyncio.to_thread(
                self.executor.execute,
                workspace_path,
            )

            success = (
                result.status
                == ExecutionStatus.SUCCESS
            )

            print("*******************************************************")
            print(result)
            print("*******************************************************")

            return ToolResult(
                success=success,
                output={
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_code": result.exit_code,
                    "status": result.status.value,
                    "timed_out": result.timed_out,
                    "oom_killed": result.oom_killed,
                    "execution_time": result.execution_time,
                },
                error=(
                    result.stderr
                    if not success
                    else None
                ),
            )

        except Exception as exc:

            return ToolResult(
                success=False,
                output=None,
                error=str(exc),
            )

        finally:

            workspace.cleanup()