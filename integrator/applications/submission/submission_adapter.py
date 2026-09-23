from abc import ABC, abstractmethod
from typing import Any

from integrator.applications.submission.submission_result import (
    SubmissionResult,
)


class SubmissionAdapter(ABC):
    """
    Interface for legitimate application submission mechanisms.

    Implementations may use an official API or another permitted
    submission mechanism.

    This interface must never bypass CAPTCHA, authentication,
    anti-bot protections, or manual verification.
    """

    name = "unknown"

    @abstractmethod
    def submit(
        self,
        job: dict[str, Any],
        application: dict[str, Any],
    ) -> SubmissionResult:
        raise NotImplementedError
