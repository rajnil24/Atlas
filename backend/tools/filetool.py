from backend.tools.base_tools import BaseTool
from pydantic import BaseModel
from backend.tools.base_tools import ToolResult
from pathlib import Path
from pypdf import PdfReader
from docx import Document

class FileToolInput(BaseModel) :
    operation: str
    path: str
    content: str | None = None

class FileTool(BaseTool) :
    tool_name = "file"
    input_schema = FileToolInput
    tool_description = """
- Use this tool whenever the user wants to read, create, update, list, or delete files.
This tool ONLY accesses files within the workspace directory.
All paths are relative to the workspace.
Never provide absolute paths.
Never use ".." or parent-directory traversal.
Supported operations:

1. read
   Read the contents of a file.
   Input:
   {
       "operation": "read",
       "path": "notes.txt"
   }

2. write
   Create or overwrite a text file.
   Input:
   {
       "operation": "write",
       "path": "notes.txt",
       "content": "Hello Atlas"
   }

3. list
   List all files and folders in a directory.
   Input:
   {
       "operation": "list",
       "path": "."
   }

4. mkdir
   Create a new directory.
   Input:
   {
       "operation": "mkdir",
       "path": "Projects"
   }

5. delete
   Delete a file.
   Input:
   {
       "operation": "delete",
       "path": "old_notes.txt"
   }
Rules:
- If the user asks about the contents of a file, first read the file, then let the LLM answer using the returned text.
- Do not use this tool for audios , images , videos.
"""
    
    def __init__(self) :
        self.workspace = Path("workspace")
        self.operations = {
            "read": self.read_file,
            "write": self.write_file,
            "list": self.list_directory,
            "mkdir": self.create_directory,
            "delete": self.delete_file
        }
        self.readers = {
            ".txt": self.read_text_file,
            ".md": self.read_text_file,
            ".pdf": self.read_pdf_file,
            ".docx": self.read_docx_file
        }
        
    def run(self , input_data : FileToolInput) -> ToolResult :
        print("inside run")
        print(input_data)
        print(type(input_data))
        operation = input_data.operation
        handler = self.operations.get(operation)
        if handler is None :
            return ToolResult(
                success = False ,
                output = f"Unsupported Operation : {operation}"
            )
        return handler(input_data)
    
    def read_file(self , input_data : FileToolInput) -> ToolResult :
        path = self.workspace / input_data.path
        if not path.exists() :
            return ToolResult(
                success=False,
                error="File does not exist."
            )
        if not path.is_file() :
            return ToolResult(
                success=False,
                error="Path is not a file."
            )
        reader = self.readers.get(path.suffix.lower())
        if reader is None :
            return ToolResult(
            success=False,
            error=f"Unsupported file type: {path.suffix}"
        )
        return reader(path)
    
    def read_text_file(self , path : Path) -> ToolResult :
        content = path.read_text(encoding = "utf-8")
        return ToolResult(
            success = True ,
            output = content
        )
    def read_pdf_file(self,path: Path) -> ToolResult:
        reader = PdfReader(path)
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
               pages.append(text)
        return ToolResult(
        success=True,
        output="\n".join(pages)
        )
    
    def read_docx_file( self,path: Path) -> ToolResult:
        document = Document(path)
        paragraphs = []
        for para in document.paragraphs:
            if para.text.strip():
               paragraphs.append(
               para.text
            )
        return ToolResult(
        success=True,
        output="\n".join(paragraphs)
        )

    def write_file(self , input_data : FileToolInput)-> ToolResult :
        path = self.workspace / input_data.path
        content = input_data.content
        path.write_text(
            content,
            encoding="utf-8"
        )
        return ToolResult(
            success=True,
            output=f"Successfully wrote to {input_data.path}"
        )
    
    def list_directory(self, input_data: FileToolInput) -> ToolResult:
        folder = self.workspace / input_data.path
        if not folder.exists():
            return ToolResult(
                success=False,
                error="Directory does not exist."
            )
        if not folder.is_dir():
            return ToolResult(
                success=False,
                error="Path is not a directory."
            )
        files = []
        for item in folder.iterdir():
            if item.is_dir():
                files.append(item.name + "/")
            else:
                files.append(item.name)
        return ToolResult(
            success=True,
            output="\n".join(files)
        )
    
    def create_directory(self, input_data: FileToolInput) -> ToolResult:
        folder = self.workspace / input_data.path
        folder.mkdir(
            parents=True,
            exist_ok=True
        )
        return ToolResult(
            success=True,
            output=f"Directory '{input_data.path}' created."
        )
    
    def delete_file(self, input_data: FileToolInput) -> ToolResult:
        path = self.workspace / input_data.path
        if not path.exists():
            print("returned from filetool.py line 145")
            return ToolResult(
                success=False,
                error="File does not exist."
            )
        if path.is_dir():
            print("returned from filetool.py line 150")
            return ToolResult(
                success=False,
                error="Delete operation currently supports files only."
            )
        path.unlink()
        return ToolResult(
            success=True,
            output=f"Deleted {input_data.path}"
        )


    
