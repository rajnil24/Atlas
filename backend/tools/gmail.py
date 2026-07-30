from pydantic import BaseModel
from googleapiclient.discovery import build
from backend.google.authenticate import authenticate
from backend.tools.base_tools import BaseTool
from backend.tools.base_tools import ToolResult
import base64
from email.mime.text import MIMEText

class GmailToolInput(BaseModel):
    operation: str
    to: str | None = None
    subject: str | None = None
    body: str | None = None
    query: str | None = None
    message_id: str | None = None

class GmailTool(BaseTool):

    tool_name = "gmail"
    input_schema = GmailToolInput
    tool_description = """
Use this tool whenever the user wants to interact with Gmail.
Use this tool whenever the user asks to send an email.

Supported operations:

1. send
Send an email.
Input:
{{
    "operation": "send",
    "to": "alice@example.com",
    "subject": "Meeting",
    "body": "Let's meet tomorrow."
}}

Rules:
- If "to" is empty , ask user to provide it .
- The planner should provide recipient, subject and body whenever available.
- If the user clearly specifies email content, use this tool instead of the LLM tool.
"""
    
    def __init__(self):
        self.creds = authenticate()
        self.service = build(
        "gmail",
        "v1",
        credentials=self.creds
        )
        self.operations = {
        "send": self.send_email,
        #"read": self.read_email,
        "search": self.search_email
        #"delete": self.delete_email,
        #"list_labels": self.list_labels,
        #"mark_read": self.mark_read,
        #"mark_unread": self.mark_unread,
        }
    
    def run(self, input_data: GmailToolInput) -> ToolResult:

        handler = self.operations.get(input_data.operation)
        if handler is None:
            return ToolResult(
            success=False,
            error=f"Unsupported operation: {input_data.operation}"
            )
        return handler(input_data)
    
    def send_email(self,input_data: GmailToolInput) -> ToolResult:
        message = MIMEText(input_data.body) # package done as MIME object
        print(type(message))
        print(message)
        message["to"] = input_data.to
        message["subject"] = input_data.subject   
        raw_message = base64.urlsafe_b64encode(   # Binary to Base 64 text encoding , and ready to dispatch
                      message.as_bytes()
                    ).decode()
        self.service.users().messages().send(
                    userId="me",
                    body={
                    "raw": raw_message
                    }
).execute()
        
    def search_email(self, input_data: GmailToolInput) -> ToolResult:
        results = self.service.users().messages().list(
        userId="me",
        q=input_data.query
        ).execute()

        messages = results.get("messages", [])

        if not messages:
            return ToolResult(
            success=True,
            output="No emails found."
        )

        return ToolResult(
        success=True,
        output=messages
        )
    

        
        