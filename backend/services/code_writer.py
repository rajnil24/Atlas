from backend.prompts.code_writer_prompt import CODE_WRITER_PROMPT
from backend.services.llm import LLMClient
from backend.tools.base_tools import BaseTool
from backend.tools.base_tools import ToolResult
from pydantic import BaseModel

class CodeWriterInput(BaseModel) :
    task : str 
    language : str 

class CodeWriterOutput(BaseModel) :
    code : str 

class CodeWriterTool(BaseTool) :
    tool_name = "code_writer"
    input_schema = CodeWriterInput
    tool_description = """
Input Schema: <task : string, language : string>.

Generates executable source code for the requested task in the specified programming language.

Use this tool BEFORE any language runtime tool whenever executable source code must be generated from a natural language task.

Supported languages include Python, C, C++, Java, TypeScript, JavaScript and many others.

Returns ONLY raw source code without markdown, explanations, or additional text.

Use this tool whenever a task requires generating source code for computation, data processing, scripting, file generation, automation, algorithms, or language-specific libraries a processing, file generation, scripting or code libraries.


"""

    def __init__(self) :
        self.llm = LLMClient()

    def clean_code(self,code: str) -> str:
        code = code.strip()
        if code.startswith("```"):
            lines = code.splitlines()
            if lines:
               lines = lines[1:]
            if lines and lines[-1].startswith("```"):
               lines = lines[:-1]
            code = "\n".join(lines)
        return code.strip()

    async def run(self , input_data : CodeWriterInput) ->ToolResult :
        code_builder_prompt =  CODE_WRITER_PROMPT.format(
            task = input_data.task ,
            language = input_data.language
        )
        #print("inside code_wrt")
        #print(type(code_builder_prompt))
        #print(code_builder_prompt)
        generated_code = await self.llm.generate(code_builder_prompt)
        #print(generated_code)  
        code = self.clean_code(generated_code)
        #print(code)
        #print(repr(code))
        return ToolResult(
            success = True ,
            output = code ,
        )

   

