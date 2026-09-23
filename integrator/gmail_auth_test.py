import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://mail.google.com/"
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CREDENTIALS_FILE = os.path.join(
    BASE_DIR,
    "credentials.json",
)

TOKEN_FILE = os.path.join(
    BASE_DIR,
    "token.json",
)


def main():
    credentials = None

    if os.path.exists(TOKEN_FILE):
        credentials = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES,
        )

    if not credentials or not credentials.valid:
        if (
            credentials
            and credentials.expired
            and credentials.refresh_token
        ):
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES,
            )

            credentials = flow.run_local_server(
                port=0
            )

        with open(TOKEN_FILE, "w") as token:
            token.write(credentials.to_json())

    gmail = build(
        "gmail",
        "v1",
        credentials=credentials,
    )

    profile = (
        gmail.users()
        .getProfile(userId="me")
        .execute()
    )

    print()
    print("=== GMAIL AUTHENTICATION SUCCESS ===")
    print()
    print("Email:", profile.get("emailAddress"))
    print("Messages:", profile.get("messagesTotal"))
    print("Threads:", profile.get("threadsTotal"))
    print()
    print("Full Gmail API access is working.")


if __name__ == "__main__":
    main()
