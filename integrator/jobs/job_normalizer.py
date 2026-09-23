from typing import Any


REQUIRED_FIELDS = {
    "title",
    "company",
    "location",
    "source",
    "application_url",
}


def normalize_job(
    raw: dict[str, Any],
    source: str,
) -> dict[str, Any]:
    """
    Convert a source-specific job dictionary into the
    normalized format used by Dickson's autoAI.
    """

    title = str(raw.get("title") or "").strip()
    company = str(raw.get("company") or "").strip()
    location = str(raw.get("location") or "").strip()
    application_url = str(
        raw.get("application_url") or ""
    ).strip()

    if not title:
        raise ValueError("Job is missing a title")

    return {
        "title": title,
        "company": company or None,
        "location": location or None,
        "source": source,
        "application_url": application_url or None,
        "description": raw.get("description"),
        "requirements": raw.get("requirements"),
    }
