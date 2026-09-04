from datetime import datetime, timezone
from typing import Optional
from googleapiclient.discovery import build
from backend.tools.base_tools import ToolResult , BaseTool
from pydantic import BaseModel
from backend.google.authenticate import authenticate

class CalendarInput(BaseModel) :
    operation: str
    max_results: int = 10
    summary: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    event_id: Optional[str] = None

class CalendarTool(BaseTool) :
    tool_name = "calendar" 
    tool_description = """
Use this tool whenever the user asks to schedule, modify,
delete, or view Google calendar events.

Supported Operations
1. Read upcoming events
{{
    "operation": "read",
    "max_results": 10
}}

2. Create a calendar event
{{
    "operation": "create",
    "summary": "ML Interview",
    "description": "Google Interview",
    "location": "Google Meet",
    "start_time": "2026-07-25T10:00:00+05:30",
    "end_time": "2026-07-25T11:00:00+05:30"
}}

3. Update an existing event
{{
    "operation": "update",
    "event_id": "...",
    "summary": "...",
    "description": "...",
    "location": "...",
    "start_time": "...",
    "end_time": "..."
}}

4. Delete an event
{{
    "operation": "delete",
    "event_id": "..."
}}

5. List all calendars
{{
    "operation": "list"
}}

Rules
- Do NOT use this tool for emails or files.
- All timestamps must be ISO-8601 format.
"""
    input_schema = CalendarInput
    
    
    def __init__(self):
        self.creds = None
        self.service = None  
        self.operations = {
            "read": self.read_events,
            "create": self.create_event,
            "update": self.update_event,
            "delete": self.delete_event,
            "list": self.list_calendars
        }

    def _get_service(self):
            if self.service is None:
                self.creds = authenticate()
                self.service = build( "calendar", "v3", credentials=self.creds)
            return self.service
    
    async def run(self, input_data: CalendarInput) -> ToolResult:
        #print("inside run calendar.py")
        operation = input_data.operation
        handler = self.operations.get(operation)
        
        if handler is None:
            return ToolResult(
                success=False,
                error=f"Unsupported operation : {operation}"
            )
        return handler(input_data)
    
    def read_events(self,input_data: CalendarInput) -> ToolResult:
        service = self._get_service()
        now = datetime.now(
            timezone.utc
        ).isoformat()
        response = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=input_data.max_results,
                singleEvents=True,
                orderBy="startTime"
            )
            .execute()
        )
        events = response.get("items", [])
        if not events:
            return ToolResult(
                success=True,
                output="No upcoming events found."
            )
        formatted_events = []
        for event in events:
            start = event["start"].get(
                "dateTime",
                event["start"].get("date")
            )
            formatted_events.append(
                {
                    "id": event["id"],
                    "summary": event.get(
                        "summary",
                        "No Title"
                    ),
                    "start": start
                }
            )
        return ToolResult(
            success=True,
            output=formatted_events
        )
    
    def create_event(self,input_data: CalendarInput ) -> ToolResult:
        service = self._get_service()
        body = {
            "summary": input_data.summary,
            "description": input_data.description,
            "location": input_data.location,
            "start": {
                "dateTime": input_data.start_time,
                "timeZone": "Asia/Kolkata"
            },
            "end": {
                "dateTime": input_data.end_time,
                "timeZone": "Asia/Kolkata"
            }
        }
        created_event = (
            service.events()
            .insert(
                calendarId="primary",
                body=body
            )
            .execute()
        )
        return ToolResult(
            success=True,
            output={
                "message": "Event Created Successfully",
                "event_id": created_event["id"],
                "link": created_event["htmlLink"]
            }
        )
    
    def find_event(self,summary: str):
        service = self._get_service()
        now = datetime.now(timezone.utc).isoformat()
        response = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            singleEvents=True,
            orderBy="startTime"
            )
        .execute()
        )
        events = response.get("items", [])
        for event in events:
            if ( event.get("summary","").lower()==summary.lower()):
                return event
        return None
    
    def update_event(self,input_data: CalendarInput) -> ToolResult:
        service = self._get_service()
        event = self.find_event(input_data.summary)
        if event is None:
            return ToolResult(
            success=False,
            error="Event not found."
            )
        if input_data.description is not None:
            event["description"] = input_data.description

        if input_data.location is not None:
            event["location"] = input_data.location

        if input_data.start_time is not None:
            event["start"] = {
            "dateTime": input_data.start_time,
            "timeZone": "Asia/Kolkata"
            }

        if input_data.end_time is not None:
            event["end"] = {
            "dateTime": input_data.end_time,
            "timeZone": "Asia/Kolkata"
            }

        if input_data.summary is not None:
            event["summary"] = input_data.summary

        updated = (
        service.events()
        .update(
            calendarId="primary",
            eventId=event["id"],
            body=event
            )
        .execute()
        )
        return ToolResult(
        success=True,
        output={
            "message": "Event Updated",
            "event_id": updated["id"]
        }
    )

    def delete_event(self,input_data: CalendarInput) -> ToolResult:
        service = self._get_service()
        event = self.find_event(input_data.summary)
        if event is None:
            return ToolResult(
            success=False,
            error="Event not found."
        )
        (
        service.events()
        .delete(
            calendarId="primary",
            eventId=event["id"]
        )
        .execute()
    )
        return ToolResult(
        success=True,
        output=f"{input_data.summary} deleted successfully."
    )

    def list_calendars(self,input_data: CalendarInput) -> ToolResult:
        service = self._get_service()
        response = (
        service.calendarList()
        .list()
        .execute()
        )
        calendars = response.get(
        "items",
        []
        )
        result = []
        for calendar in calendars:
            result.append(
            {
                "id": calendar["id"],
                "name": calendar["summary"]
            }
        )
        return ToolResult(
        success=True,
        output=result
    )