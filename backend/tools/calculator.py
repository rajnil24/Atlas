from pydantic import BaseModel

from backend.tools.base_tools import BaseTool, ToolResult


class CalculatorInput(BaseModel):
    expression: str


class CalculatorTool(BaseTool):

    tool_name = "calculator"
    tool_description =  " Input: {{expression: <mathematical expression>}} Performs arithmetic calculations."
    input_schema = CalculatorInput

    def run(
        self,
        input_data: CalculatorInput
    ) -> ToolResult:

        expression = input_data.expression

        try:
            answer = eval(expression)
            return ToolResult(
                success=True,
                output=answer
            )
        except Exception as e:
            print("returned from calculator.py line30")
            return ToolResult(
                success=False,
                error=str(e)
            )