from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json

from integrator.jobs.job_source import JobSource


class GreenhouseJobSource(JobSource):
    """
    Fetch published jobs from a Greenhouse public job board.

    Configuration format:
        GreenhouseJobSource("board_token")
        GreenhouseJobSource("board_token", "Company Name")
    """

    name = "greenhouse"

    def __init__(
        self,
        board_token: str,
        company_name: str | None = None,
    ):
        self.board_token = board_token.strip()

        if not self.board_token:
            raise ValueError(
                "Greenhouse board token cannot be empty"
            )

        self.company_name = (
            company_name.strip()
            if company_name
            else None
        )

    @property
    def url(self) -> str:
        params = urlencode({"content": "true"})

        return (
            "https://boards-api.greenhouse.io/v1/boards/"
            f"{self.board_token}/jobs?{params}"
        )

    def fetch_jobs(self) -> list[dict[str, Any]]:
        request = Request(
            self.url,
            headers={
                "Accept": "application/json",
                "User-Agent": "Dicksons-autoAI/1.0",
            },
            method="GET",
        )

        try:
            with urlopen(request, timeout=20) as response:
                payload = json.load(response)

        except HTTPError as exc:
            raise RuntimeError(
                f"Greenhouse returned HTTP {exc.code} "
                f"for board '{self.board_token}'"
            ) from exc

        except URLError as exc:
            raise RuntimeError(
                f"Could not reach Greenhouse board "
                f"'{self.board_token}': {exc.reason}"
            ) from exc

        except TimeoutError as exc:
            raise RuntimeError(
                f"Greenhouse request timed out for "
                f"board '{self.board_token}'"
            ) from exc

        jobs = payload.get("jobs", [])

        return [
            self._convert_job(job)
            for job in jobs
        ]

    def _convert_job(
        self,
        job: dict[str, Any],
    ) -> dict[str, Any]:

        location = (
            (job.get("location") or {}).get("name")
            or ""
        )

        absolute_url = (
            job.get("absolute_url")
            or ""
        )

        company = self._company_name(job)

        return {
            "title": job.get("title"),
            "company": company,
            "location": location,
            "application_url": absolute_url,
            "description": job.get("content"),
            "requirements": None,
        }

    def _company_name(
        self,
        job: dict[str, Any],
    ) -> str | None:

        # Prefer explicitly configured company name.
        if self.company_name:
            return self.company_name

        # Otherwise use company information if the
        # Greenhouse response happens to provide it.
        company = job.get("company")

        if isinstance(company, dict):
            return company.get("name")

        if company:
            return str(company)

        return None
