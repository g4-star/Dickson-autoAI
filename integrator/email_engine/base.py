from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class EmailMessage:
    provider_message_id: str
    sender: str
    recipient: Optional[str]
    subject: str
    body: str
    received_at: datetime
    thread_id: Optional[str] = None


class EmailProvider(ABC):
    """
    Provider-neutral interface for mailbox integrations.

    Concrete providers such as Gmail or IMAP implement these methods.
    """

    @abstractmethod
    def test_connection(self) -> bool:
        """Return True when the mailbox connection is usable."""
        raise NotImplementedError

    @abstractmethod
    def fetch_messages(
        self,
        *,
        limit: int = 50,
    ) -> list[EmailMessage]:
        """Fetch recent messages from the mailbox."""
        raise NotImplementedError
