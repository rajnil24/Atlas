from typing import Literal
from pydantic import BaseModel
from backend.tools.base_tools import BaseTool
from backend.tools.base_tools import ToolResult
from backend.config import GROQ_API_KEY 
from groq import Groq 

class LLMToolInput(BaseModel):
    operation: Literal[
        "summarize",
        "explain",
        "rewrite",
        "report",
        "translate",
        "answer",
        "format"
    ]
    text: str
    instruction: str | None = None

class LLMTool(BaseTool) :
    def __init__(self):
        self.client = Groq(
        api_key= GROQ_API_KEY
    )
        self.model = "llama-3.3-70b-versatile"
    
    tool_name = "llm_tool"
    tool_description = """
Use it whenever previous tool outputs need to be rewritten, summarized, explained, translated, formatted, or converted into well-written natural language.
Use this tool whenever information needs to be transformed into another form using reasoning or natural language generation.
This tool should NOT be used to retrieve information from the internet, perform arithmetic calculations, read files, or obtain any other information.

Typical use cases:
• Convert structured data into a readable report.
• Summarize long text.
• Explain technical content.
• Rewrite text professionally.
• Translate text.
• Format information into Markdown.
• Generate human-readable documents before writing them into files.

Input Schema
{{
    "operation": "...",
    "text": "...",
}}

Supported Operations

summarize
Explain the important points briefly.

Example

{{
    "operation": "summarize",
    "text": "{{step_1.output}}"
}}
----------------------------------------------------
report
Generate a professional report from structured information.

Example
{{
    "operation": "report",
    "text": "{{step_2.output}}"
}}
----------------------------------------------------
explain
Explain information in detail.

Example
{{
    "operation": "explain",
    "text": "{{step_5.output}}"
}}
----------------------------------------------------
rewrite
Rewrite the supplied text professionally.

Example
{{
    "operation": "rewrite",
    "text": "{{step_1.output}}"
}}
----------------------------------------------------
translate
Translate the supplied text.
Use instruction to specify the target language.

Example
{{
    "operation": "translate",
    "text": "{{step_4.output}}",
    "instruction": "French"
}}
----------------------------------------------------
format
Format text according to instruction.

Example
{{
    "operation": "format",
    "text": "{{step_2.output}}",
    "instruction": "Markdown"
}}
----------------------------------------------------
answer
Generate a natural language answer using information from previous tool outputs.

Example
{{
    "operation": "answer",
    "text": "{{step_1.output}}"
}}


• Use this tool whenever information must be transformed before presenting it to the user.
• Use this tool before the File Tool if the user requests a document, report, notes, summary, or other formatted content.
• Do not use this tool for calculations.
• Do not use this tool for retrieving external information.
• Do not use this tool when another specialized tool can directly solve the request.
"""
    input_schema = LLMToolInput

    def run(self , input_data : LLMToolInput)->ToolResult :
        prompts = {
        "summarize" :"""
        Summarize the following text.
        Keep only the important information.
        Text:{text}
        """ ,

        "explain":
        """
        Explain the following text clearly.
        Text:{text}
        """ ,

        "rewrite":
        """
        Rewrite the following text professionally.
        Text:{text}
        """,

        "report":
        """
        Create a well-structured professional report using the following information.
        Use headings where appropriate.
        Present the information naturally.
        Do not mention JSON or dictionaries.
        Text:{text}
        """,

        "translate":
        """
        Translate the following text.
        Target Language:{instruction}
        Text:{text}
        """,

        "format":
        """
        Format the following text.
        Formatting Instruction:{instruction}
        Text:{text}
        """,

        "answer":
        """
        Using only the information below,
        generate a clear natural language answer.
        Information:{text}
        """
        }
        if input_data.operation not in prompts:
            print("returned from llm_tool.py line168")
            return ToolResult(
            success=False,
            error=f"Unsupported operation: {input_data.operation}"
        )
        prompt = prompts[input_data.operation].format(
        text=input_data.text,
        instruction=input_data.instruction or ""
        )
        print("prompt inside llm_tool.py is ----" )
        print(prompt)
        response = self.client.chat.completions.create(
        model=self.model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
        output = response.choices[0].message.content
        return ToolResult(
        success=True,
        output=output
    )

