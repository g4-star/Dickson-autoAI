from dataclasses import dataclass
from typing import Any

from integrator.ai.matching.application_decision import (
    ApplicationDecision,
)


@dataclass
class ApplicationDecisionResult:
    allowed: bool
    reason: str


class ApplicationEngine:
    """
    Final gate controlling whether an application may proceed.

    This layer enforces operational conditions such as:

    - auto-apply enabled
    - daily target
    - application URL
    - duplicate prevention
    - fitness threshold

    It does not bypass CAPTCHA, authentication,
    anti-bot controls, or manual verification.
    """

    def can_apply(
        self,
        job: dict[str, Any],
        settings: dict[str, Any],
        applications_today: int,
        existing_applications: list[dict[str, Any]],
        application_decision: ApplicationDecision,
    ) -> ApplicationDecisionResult:

        if not settings.get("auto_apply", False):
            return ApplicationDecisionResult(
                allowed=False,
                reason="Automatic application is disabled",
            )

        target = settings.get(
            "daily_application_target",
            0,
        )

        if applications_today >= target:
            return ApplicationDecisionResult(
                allowed=False,
                reason=(
                    "Daily application target "
                    "has been reached"
                ),
            )

        if not job.get("application_url"):
            return ApplicationDecisionResult(
                allowed=False,
                reason=(
                    "No application URL is available"
                ),
            )

        if not application_decision.apply:
            return ApplicationDecisionResult(
                allowed=False,
                reason=(
                    "Application blocked: fitness score "
                    f"{application_decision.fitness_score}% is below "
                    f"the {application_decision.threshold}% threshold."
                ),
            )

        job_id = job.get("id")

        for application in existing_applications:
            if application.get("job_id") == job_id:
                return ApplicationDecisionResult(
                    allowed=False,
                    reason=(
                        "Application already exists "
                        "for this job"
                    ),
                )

        return ApplicationDecisionResult(
            allowed=True,
            reason=(
                "Application passed the automation gate "
                f"with fitness score "
                f"{application_decision.fitness_score}%."
            ),
        )
