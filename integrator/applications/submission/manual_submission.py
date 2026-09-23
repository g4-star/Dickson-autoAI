from typing import Any

from integrator.applications.submission.submission_adapter import (
    SubmissionAdapter,
)
from integrator.applications.submission.submission_result import (
    SubmissionResult,
)


class ManualSubmissionAdapter(SubmissionAdapter):
    """
    Stops the automated workflow and hands the application
    to the user when automated submission is unavailable.
    """

    name = "manual"

    def submit(
        self,
        job: dict[str, Any],
        application: dict[str, Any],
    ) -> SubmissionResult:

        title = job.get("title") or "Unknown job"
        company = job.get("company") or "Unknown company"

        return SubmissionResult(
            status="manual_action_required",
            message=(
                f"Manual submission required for "
                f"{title} at {company}."
            ),
            requires_manual_action=True,
        )
