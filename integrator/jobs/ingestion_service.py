import logging
from typing import Any

from integrator.api_client import AutoAIClient
from integrator.jobs.job_deduplicator import JobDeduplicator
from integrator.jobs.job_normalizer import normalize_job
from integrator.jobs.source_registry import JobSourceRegistry


class JobIngestionService:
    """
    Fetches jobs from registered sources, normalizes them,
    removes duplicates, and stores new listings in the backend.
    """

    def __init__(
        self,
        client: AutoAIClient,
        registry: JobSourceRegistry,
    ):
        self.client = client
        self.registry = registry
        self.deduplicator = JobDeduplicator()

    def ingest(self, user_id: int) -> dict[str, Any]:

        raw_jobs = self.registry.fetch_all()

        normalized_jobs = []

        for raw_job in raw_jobs:
            try:
                normalized_jobs.append(
                    normalize_job(
                        raw_job,
                        raw_job.get("source", "unknown"),
                    )
                )
            except Exception as exc:
                logging.error(
                    "Job normalization failed: %s",
                    exc,
                )

        unique_jobs = self.deduplicator.deduplicate(
            normalized_jobs
        )

        existing_jobs = self.client.get_jobs(user_id)

        existing_urls = {
            (job.get("application_url") or "").strip().lower()
            for job in existing_jobs
            if job.get("application_url")
        }

        created = 0
        skipped = 0

        for job in unique_jobs:

            application_url = (
                job.get("application_url") or ""
            ).strip().lower()

            if application_url and application_url in existing_urls:
                skipped += 1
                continue

            try:
                self.client.create_job(
                    user_id,
                    job,
                )

                created += 1

                if application_url:
                    existing_urls.add(application_url)

            except Exception as exc:
                logging.error(
                    "Failed to store job %s: %s",
                    job.get("title"),
                    exc,
                )

        return {
            "raw": len(raw_jobs),
            "normalized": len(normalized_jobs),
            "unique": len(unique_jobs),
            "created": created,
            "skipped": skipped,
        }
