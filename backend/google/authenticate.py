from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from pathlib import Path

def authenticate():
        credentials_file = Path("backend/google/credentials.json")
        token_file = Path("backend/google/token.json")
        creds = None
        SCOPES = [
        "https://www.googleapis.com/auth/calendar" , 
        "https://www.googleapis.com/auth/gmail.modify"
        ]
        if token_file.exists():
            creds = Credentials.from_authorized_user_file(
                token_file,
                SCOPES
            )

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file,
                    SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open(token_file, "w") as token:
                token.write(
                    creds.to_json()
                )
        return creds 