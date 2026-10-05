from backend.tools.code_execution_tool import CodeExecutionInput , CodeExecutionTool
from backend.tools.base_tools import ToolResult
import asyncio
tool = CodeExecutionTool()

code = """
from pathlib import Path

try:
    Path("/tmp/hello.txt").write_text("hello")
    print("TMP WRITE SUCCEEDED")
    print(Path("/tmp/hello.txt").read_text())
except Exception as e:
    print("TMP WRITE FAILED")
    print(type(e).__name__)
    print(str(e))
"""
input = CodeExecutionInput(code = code , )
result = asyncio.run(tool.run(input))
print(result)
print("ff.py line 19")

