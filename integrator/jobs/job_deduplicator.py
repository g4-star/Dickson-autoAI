from typing import Any


class JobDeduplicator:
    """
    Removes duplicate job listings.

    Application URLs are preferred as the unique identity.
    A title/company/location fallback is used when a URL
    isn't available.
    """

    def deduplicate(
        self,
        jobs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        seen = set()
        result = []

        for job in jobs:

            application_url = job.get("application_url")

            if application_url:
                key = (
                    "url",
                    application_url.strip().lower(),
                )
            else:
                key = (
                    "job",
                    (job.get("title") or "").strip().lower(),
                    (job.get("company") or "").strip().lower(),
                    (job.get("location") or "").strip().lower(),
                )

            if key in seen:
                continue

            seen.add(key)
            result.append(job)

        return result
