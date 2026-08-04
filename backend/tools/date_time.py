from datetime import datetime
from pydantic import BaseModel
from backend.tools.base_tools import BaseTool, ToolResult


class DateTimeInput(BaseModel):
    operation: str


class DateTimeTool(BaseTool):

    tool_name = "datetime"
    tool_description = ("Input:{{ operation: <operation>}}"
        "Returns current date and time information. "
        "Supported operations: "
        "date, time, year, month, day, weekday."
    )

    input_schema = DateTimeInput

    async def run(
        self,
        input_data: DateTimeInput
    ) -> ToolResult:

        now = datetime.now()
        operation = input_data.operation.lower()
        if operation == "date":
            result = now.strftime("%Y-%m-%d")
        elif operation == "time":
            result = now.strftime("%H:%M:%S")
        elif operation == "year":
            result = now.year
        elif operation == "month":
            result = now.strftime("%B")
        elif operation == "day":
            result = now.day
        elif operation == "weekday":
            result = now.strftime("%A")
        else:
            return ToolResult(
                success=False,
                error=f"Unknown operation '{operation}'"
            )
        return ToolResult(
            success=True,
            output=result
        )