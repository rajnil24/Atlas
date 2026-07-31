from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timezone

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly"
]
# it says I allowed Atlas to make calls
CREDENTIALS_FILE = Path(__file__).parent / "credentials.json" 
TOKEN_FILE = Path(__file__).parent / "token.json"   # I am an authenticated user

creds = None
if TOKEN_FILE.exists():
    creds = Credentials.from_authorized_user_file(
        TOKEN_FILE,
        SCOPES
    )

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE,
            SCOPES
        )
        creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, "w") as token:
        token.write(creds.to_json())

service = build(serviceName = "calendar" ,version = "v3" ,credentials = creds )
now = datetime.now(timezone.utc).isoformat()
events_result = (
    service.events()
    .list(
        calendarId="primary",
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy="startTime"
    )
    .execute()
)
events = events_result.get("items", [])
if not events:
    print("No upcoming events found.")

for event in events:

    start = event["start"].get(
        "dateTime",
        event["start"].get("date")
    )

    print(start, "-", event["summary"])