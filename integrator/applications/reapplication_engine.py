import logging
from datetime import datetime, timezone
from typing import Any

from integrator.api_client import AutoAIClient
from integrator.applications.application_preparer import (
    ApplicationPreparer,
)
from integrator.applications.submission.submission_engine import (
    SubmissionEngine,
)


class ReapplicationEngine:
    """
    Handles scheduled follow-up/reapplication attempts.

    A single Application record is reused for all attempts.
    The backend enforces max_attempts.
    """

    def __init__(
        self,
        client: AutoAIClient,
        submission_engine: SubmissionEngine,
    ):
        self.client = client
        self.submission_engine = submission_engine
        self.preparer = ApplicationPreparer()

    def is_due(
        self,
        application: dict[str, Any],
    ) -> bool:
        if application.get("status") != "follow_up_pending":
            return False

        next_action_at = application.get("next_action_at")

        if not next_action_at:
            return True

        try:
            due_time = datetime.fromisoformat(
                next_action_at.replace("Z", "+00:00")
            )

            if due_time.tzinfo is None:
                due_time = due_time.replace(
                    tzinfo=timezone.utc
                )

            return datetime.now(timezone.utc) >= due_time

        except (TypeError, ValueError):
            logging.warning(
                "Invalid next_action_at for application %s",
                application.get("id"),
            )
            return False

    def process(
        self,
        user_id: int,
        application: dict[str, Any],
        job: dict[str, Any],
        user: dict[str, Any],
    ) -> dict[str, Any]:

        application_id = application.get("id")

        if not application_id:
            return {
                "status": "failed",
                "message": "Application ID is missing",
            }

        if not self.is_due(application):
            return {
                "status": "not_due",
                "message": "Follow-up is not due yet",
            }

        try:
            prepared = self.client.start_application_follow_up(
                user_id,
                application_id,
            )
        except Exception as exc:
            logging.exception(
                "Failed to start follow-up for application %s",
                application_id,
            )
            return {
                "status": "failed",
                "message": str(exc),
            }

        if prepared.get("status") == "failed":
            return {
                "status": "failed",
                "message": prepared.get(
                    "failure_reason",
                    "Maximum application attempts reached.",
                ),
            }

        result = self.submission_engine.submit(
            user_id,
            job,
            prepared,
        )

        return result
