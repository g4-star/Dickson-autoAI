import base64
import os
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from integrator.email_engine.base import EmailMessage, EmailProvider


class GmailProvider(EmailProvider):
    """
    Read-only Gmail provider.

    Responsibilities:
    - authenticate using an existing OAuth token
    - verify Gmail connectivity
    - fetch recent Gmail messages
    - convert Gmail API messages into EmailMessage objects

    This provider intentionally does not send, delete, archive,
    or modify Gmail messages.
    """

    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly"
    ]

    def __init__(
        self,
        *,
        credentials_file: Optional[str] = None,
        token_file: Optional[str] = None,
    ):
        base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        integrator_dir = os.path.dirname(base_dir)

        self.credentials_file = credentials_file or os.path.join(
            integrator_dir,
            "credentials.json",
        )

        self.token_file = token_file or os.path.join(
            integrator_dir,
            "token.json",
        )

        self._service = None

    def _load_credentials(self) -> Credentials:
        if not os.path.exists(self.token_file):
            raise FileNotFoundError(
                f"Gmail token file not found: {self.token_file}"
            )

        credentials = Credentials.from_authorized_user_file(
            self.token_file,
            self.SCOPES,
        )

        if not credentials.valid:
            if (
                credentials.expired
                and credentials.refresh_token
            ):
                credentials.refresh(Request())

                with open(
                    self.token_file,
                    "w",
                ) as token:
                    token.write(
                        credentials.to_json()
                    )
            else:
                raise RuntimeError(
                    "Gmail credentials are invalid or expired. "
                    "Run gmail_auth_test.py again."
                )

        return credentials

    def _get_service(self):
        if self._service is None:
            credentials = self._load_credentials()

            self._service = build(
                "gmail",
                "v1",
                credentials=credentials,
            )

        return self._service

    def test_connection(self) -> bool:
        service = self._get_service()

        service.users().getProfile(
            userId="me"
        ).execute()

        return True

    def fetch_messages(
        self,
        *,
        limit: int = 50,
    ) -> list[EmailMessage]:
        if limit < 1:
            return []

        service = self._get_service()

        response = (
            service.users()
            .messages()
            .list(
                userId="me",
                maxResults=limit,
                labelIds=["INBOX"],
            )
            .execute()
        )

        message_refs = response.get(
            "messages",
            []
        )

        messages = []

        for reference in message_refs:
            message = (
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=reference["id"],
                    format="full",
                )
                .execute()
            )

            normalized = self._normalize_message(
                message
            )

            if normalized is not None:
                messages.append(normalized)

        return messages

    @classmethod
    def _normalize_message(
        cls,
        message: dict,
    ) -> Optional[EmailMessage]:
        payload = message.get(
            "payload",
            {},
        )

        headers = {
            header.get("name", "").lower():
                header.get("value", "")
            for header in payload.get(
                "headers",
                [],
            )
        }

        sender = headers.get(
            "from",
            "",
        )

        recipient = headers.get(
            "to",
        )

        subject = headers.get(
            "subject",
            "",
        )

        received_at = cls._parse_date(
            headers.get("date")
        )

        body = cls._extract_body(
            payload
        )

        return EmailMessage(
            provider_message_id=message["id"],
            sender=sender,
            recipient=recipient,
            subject=subject,
            body=body,
            received_at=received_at,
            thread_id=message.get(
                "threadId"
            ),
        )

    @staticmethod
    def _parse_date(
        value: Optional[str],
    ) -> datetime:
        if value:
            try:
                parsed = parsedate_to_datetime(
                    value
                )

                if parsed.tzinfo is None:
                    parsed = parsed.replace(
                        tzinfo=timezone.utc
                    )

                return parsed.astimezone(
                    timezone.utc
                ).replace(
                    tzinfo=None
                )

            except (TypeError, ValueError):
                pass

        return datetime.utcnow()

    @classmethod
    def _extract_body(
        cls,
        payload: dict,
    ) -> str:
        body = payload.get(
            "body",
            {},
        )

        data = body.get(
            "data"
        )

        if data:
            return cls._decode_body(
                data
            )

        for part in payload.get(
            "parts",
            [],
        ):
            result = cls._extract_body(
                part
            )

            if result:
                return result

        return ""

    @staticmethod
    def _decode_body(
        data: str,
    ) -> str:
        try:
            decoded = base64.urlsafe_b64decode(
                data.encode("utf-8")
            )

            return decoded.decode(
                "utf-8",
                errors="replace",
            )

        except (
            ValueError,
            UnicodeDecodeError,
        ):
            return ""
