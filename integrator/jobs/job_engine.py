from dataclasses import dataclass
from typing import Any


@dataclass
class JobMatch:
    job: dict[str, Any]
    score: int
    suitable: bool
    reasons: list[str]


class JobEngine:
    """
    Transparent first-stage job matching engine.

    The engine only uses information actually present
    in the user's profile and the job listing.
    """

    def evaluate(
        self,
        job: dict[str, Any],
        user: dict[str, Any],
    ) -> JobMatch:

        score = 0
        reasons = []

        title = (
            job.get("title") or ""
        ).lower()

        description = (
            job.get("description") or ""
        ).lower()

        requirements = (
            job.get("requirements") or ""
        ).lower()

        searchable_text = (
            f"{title} "
            f"{description} "
            f"{requirements}"
        )

        # -------------------------------------------------
        # Preferred roles
        # -------------------------------------------------

        preferred_roles = (
            user.get("preferred_roles") or ""
        )

        role_matches = []

        for role in preferred_roles.split(","):
            role = role.strip().lower()

            if not role:
                continue

            if role in searchable_text:
                role_matches.append(role)

        if role_matches:
            score += 40
            reasons.append(
                "Matches preferred role(s): "
                + ", ".join(role_matches)
            )

        # -------------------------------------------------
        # Work preference
        # -------------------------------------------------

        work_preference = (
            user.get("work_preference") or ""
        ).lower()

        job_location = (
            job.get("location") or ""
        ).lower()

        if work_preference:
            preference_matches = {
                "remote": [
                    "remote",
                    "work from home",
                    "wfh",
                ],
                "hybrid": [
                    "hybrid",
                ],
                "onsite": [
                    "onsite",
                    "on-site",
                    "office",
                ],
            }

            terms = preference_matches.get(
                work_preference,
                [work_preference],
            )

            if any(
                term in searchable_text
                or term in job_location
                for term in terms
            ):
                score += 20

                reasons.append(
                    "Work preference appears compatible"
                )

        # -------------------------------------------------
        # CV availability
        # -------------------------------------------------

        if user.get("cv_path"):
            score += 20
            reasons.append(
                "User CV is available"
            )

        # -------------------------------------------------
        # Basic listing quality
        # -------------------------------------------------

        if title:
            score += 10
            reasons.append(
                "Job has a valid title"
            )

        if job.get("application_url"):
            score += 10
            reasons.append(
                "Application URL is available"
            )

        score = min(score, 100)

        suitable = score >= 60

        if suitable:
            reasons.append(
                "Job passed the suitability threshold"
            )
        else:
            reasons.append(
                "Job did not meet the suitability threshold"
            )

        return JobMatch(
            job=job,
            score=score,
            suitable=suitable,
            reasons=reasons,
        )
