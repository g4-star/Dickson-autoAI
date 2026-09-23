from dataclasses import dataclass
from typing import Optional


@dataclass
class SubmissionResult:
    status: str
    message: str
    confirmation_id: Optional[str] = None
    applied_at: Optional[str] = None
    requires_manual_action: bool = False
