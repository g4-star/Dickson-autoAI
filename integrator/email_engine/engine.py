from typing import Optional

from integrator.email_engine.base import EmailProvider, EmailMessage
from integrator.email_engine.models import NormalizedEmail


class EmailEngine:
    """
    Provider-independent email orchestration.
    """

    def __init__(self, provider: EmailProvider):
        self.provider = provider

    def test_connection(self) -> bool:
        return self.provider.test_connection()

    def fetch_recent(
        self,
        *,
        limit: int = 50,
    ) -> list[NormalizedEmail]:
        messages = self.provider.fetch_messages(limit=limit)

        return [
            self._normalize(message)
            for message in messages
        ]

    def fetch_page(
        self,
        *,
        page_size: int = 100,
        page_token: Optional[str] = None,
        label_ids: Optional[list[str]] = None,
    ) -> tuple[list[NormalizedEmail], Optional[str]]:
        """
        Fetch one paginated mailbox page.

        Returns:
            normalized messages,
            next Gmail page token
        """
        fetch_page = getattr(
            self.provider,
            "fetch_message_page",
            None,
        )

        if fetch_page is None:
            messages = self.provider.fetch_messages(
                limit=page_size,
            )

            return (
                [self._normalize(message) for message in messages],
                None,
            )

        messages, next_token = fetch_page(
            page_size=page_size,
            page_token=page_token,
            label_ids=label_ids,
        )

        return (
            [self._normalize(message) for message in messages],
            next_token,
        )

    @staticmethod
    def _normalize(
        message: EmailMessage,
    ) -> NormalizedEmail:
        return NormalizedEmail(
            provider_message_id=message.provider_message_id,
            sender=message.sender,
            recipient=message.recipient,
            subject=message.subject,
            body=message.body,
            received_at=message.received_at,
            thread_id=message.thread_id,
        )
