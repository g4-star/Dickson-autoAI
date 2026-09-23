from abc import ABC, abstractmethod
from typing import Any


class JobSource(ABC):
    """
    Base interface for every job listing source.

    Each source returns normalized job dictionaries.
    """

    name = "unknown"

    @abstractmethod
    def fetch_jobs(self) -> list[dict[str, Any]]:
        """
        Fetch available jobs from the source.

        Implementations must return normalized dictionaries.
        """
        raise NotImplementedError
