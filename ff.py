from backend.tools.code_execution_tool import CodeExecutionInput , CodeExecutionTool
from backend.tools.base_tools import ToolResult
import asyncio
tool = CodeExecutionTool()

code = """
print("badiya")
"""
input = CodeExecutionInput(code = code , )
result = asyncio.run(tool.run(input))
print(result)
print("ff.py line 19")

