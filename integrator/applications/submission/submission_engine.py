import logging
from datetime import datetime, timezone
from typing import Any

from integrator.api_client import AutoAIClient
from integrator.applications.submission.manual_submission import (
    ManualSubmissionAdapter,
)


class SubmissionEngine:
    """
    Coordinates application submission.

    The engine only marks an application as submitted when
    the submission adapter provides an actual confirmation.
    """

    def __init__(self, client: AutoAIClient):
        self.client = client
        self.manual_adapter = ManualSubmissionAdapter()

    def submit(
        self,
        user_id: int,
        job: dict[str, Any],
        application: dict[str, Any],
    ) -> dict[str, Any]:

        application_id = application.get("id")

        if not application_id:
            raise ValueError("Application ID is required")

        current_status = application.get("status")

        if current_status != "prepared":
            return {
                "status": "skipped",
                "message": (
                    f"Application {application_id} is "
                    f"not ready for submission: {current_status}"
                ),
            }

        self.client.update_application(
            user_id,
            application_id,
            {
                "status": "submitting",
            },
        )

        result = self.manual_adapter.submit(
            job,
            application,
        )

        if result.requires_manual_action:
            self.client.update_application(
                user_id,
                application_id,
                {
                    "status": "manual_action_required",
                },
            )

            return {
                "status": "manual_action_required",
                "message": result.message,
            }

        if result.status != "submitted":
            self.client.update_application(
                user_id,
                application_id,
                {
                    "status": "failed",
                    "failure_reason": result.message,
                },
            )

            return {
                "status": "failed",
                "message": result.message,
            }

        applied_at = (
            result.applied_at
            or datetime.now(timezone.utc).isoformat()
        )

        self.client.update_application(
            user_id,
            application_id,
            {
                "status": "submitted",
                "applied_at": applied_at,
            },
        )

        logging.info(
            "Application %s submitted successfully",
            application_id,
        )

        return {
            "status": "submitted",
            "message": result.message,
            "confirmation_id": result.confirmation_id,
            "applied_at": applied_at,
        }
