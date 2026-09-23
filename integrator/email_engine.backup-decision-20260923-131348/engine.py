
from integrator.email_engine.base import EmailProvider, EmailMessage
from integrator.email_engine.models import NormalizedEmail


class EmailEngine:
    """
    Provider-independent email orchestration.

    Responsibilities:
    - connect to a mailbox provider
    - fetch messages
    - normalize provider-specific messages
    - return normalized messages to the persistence layer
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

    @staticmethod
    def _normalize(message: EmailMessage) -> NormalizedEmail:
        return NormalizedEmail(
            provider_message_id=message.provider_message_id,
            sender=message.sender,
            recipient=message.recipient,
            subject=message.subject,
            body=message.body,
            received_at=message.received_at,
            thread_id=message.thread_id,
        )
