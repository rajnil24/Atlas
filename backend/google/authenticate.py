from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError


def authenticate():

    credentials_file = Path("backend/google/credentials.json")
    token_file = Path("backend/google/token.json")

    SCOPES = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/gmail.modify",
    ]

    creds = None

    # --------------------------------------------------
    # 1. Load previously saved OAuth credentials
    # --------------------------------------------------

    if token_file.exists():
        creds = Credentials.from_authorized_user_file(
            token_file,
            SCOPES,
        )

    # --------------------------------------------------
    # 2. Existing credentials are invalid
    # --------------------------------------------------

    if not creds or not creds.valid:

        # Try refreshing the existing token
        if creds and creds.expired and creds.refresh_token:

            try:
                creds.refresh(Request())

            except RefreshError:
                print("Google OAuth token expired/revoked.")
                print("Starting OAuth authorization again.")

                # Old token is no longer useful
                token_file.unlink(missing_ok=True)

                creds = None

        # --------------------------------------------------
        # 3. No usable credentials → ask user to authorize
        # --------------------------------------------------

        if not creds:

            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file,
                SCOPES,
            )

            creds = flow.run_local_server(port=0)

        # --------------------------------------------------
        # 4. Save the new credentials
        # --------------------------------------------------

        with open(token_file, "w") as token:
            token.write(creds.to_json())

    return creds