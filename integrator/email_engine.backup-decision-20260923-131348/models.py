from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class NormalizedEmail:
    provider_message_id: str
    sender: str
    recipient: Optional[str]
    subject: str
    body: str
    received_at: datetime
    thread_id: Optional[str] = None
    category: Optional[str] = None
