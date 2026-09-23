from integrator.config import GREENHOUSE_BOARDS
from integrator.jobs.job_source import JobSource
from integrator.jobs.sources.greenhouse_source import (
    GreenhouseJobSource,
)
from integrator.jobs.sources.test_source import TestJobSource


class JobSourceRegistry:

    def __init__(self):
        self.sources: list[JobSource] = []

        if not GREENHOUSE_BOARDS:
            self.sources.append(TestJobSource())

        for board in GREENHOUSE_BOARDS:
            if ":" in board:
                company_name, board_token = board.split(
                    ":", 1
                )

                self.sources.append(
                    GreenhouseJobSource(
                        board_token=board_token,
                        company_name=company_name,
                    )
                )
            else:
                self.sources.append(
                    GreenhouseJobSource(board)
                )

    def fetch_all(self) -> list[dict]:
        jobs = []

        for source in self.sources:
            jobs.extend(source.fetch_jobs())

        return jobs
