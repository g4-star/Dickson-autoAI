from dataclasses import dataclass
from typing import Any

from integrator.email_engine.models import NormalizedEmail


@dataclass
class ReplyDraft:
    body: str
    confidence: float
    reason: str


class ReplyGenerator:
    """
    Conservative email reply generator.

    This component generates drafts only.
    It does NOT send email.

    Facts must come from the supplied candidate profile.
    It must never invent qualifications, experience,
    availability, salary, education, or other personal facts.
    """

    def generate(
        self,
        *,
        message: NormalizedEmail,
        candidate_profile: dict[str, Any],
    ) -> ReplyDraft:

        category = self._detect_category(message)

        if category == "job/recruiter":
            return self._generate_recruiter_reply(
                message=message,
                candidate_profile=candidate_profile,
            )

        if category == "school/class":
            return self._generate_school_reply(
                message=message,
            )

        if category == "client":
            return self._generate_client_reply(
                message=message,
            )

        return ReplyDraft(
            body="",
            confidence=0.0,
            reason="No safe reply template available.",
        )

    def _generate_recruiter_reply(
        self,
        *,
        message: NormalizedEmail,
        candidate_profile: dict[str, Any],
    ) -> ReplyDraft:

        name = candidate_profile.get("name")

        if not name:
            name = "Dickson"

        # We deliberately do not claim:
        # - years of experience
        # - specific qualifications
        # - salary expectations
        # - availability
        # - interview acceptance
        #
        # unless those facts are explicitly supplied.

        body = (
            f"Hello,\n\n"
            f"Thank you for reaching out regarding the opportunity.\n\n"
            f"I am interested in learning more about the role. "
            f"Could you please share the job description and the "
            f"next steps in the recruitment process?\n\n"
            f"Kind regards,\n"
            f"{name}"
        )

        return ReplyDraft(
            body=body,
            confidence=0.90,
            reason=(
                "Generated a conservative recruitment response "
                "without making unsupported claims."
            ),
        )

    def _generate_school_reply(
        self,
        *,
        message: NormalizedEmail,
    ) -> ReplyDraft:

        body = (
            "Hello,\n\n"
            "Thank you for the message. I have received it and "
            "will review the information provided.\n\n"
            "Kind regards,\n"
            "Dickson"
        )

        return ReplyDraft(
            body=body,
            confidence=0.85,
            reason="Generated a simple acknowledgement without inventing facts.",
        )

    def _generate_client_reply(
        self,
        *,
        message: NormalizedEmail,
    ) -> ReplyDraft:

        body = (
            "Hello,\n\n"
            "Thank you for reaching out. I would be happy to "
            "learn more about the project and your requirements.\n\n"
            "Please share the relevant details, and we can discuss "
            "the next steps.\n\n"
            "Kind regards,\n"
            "Dickson"
        )

        return ReplyDraft(
            body=body,
            confidence=0.85,
            reason="Generated a conservative client response.",
        )

    @staticmethod
    def _detect_category(
        message: NormalizedEmail,
    ) -> str:

        text = " ".join(
            [
                message.sender or "",
                message.subject or "",
                message.body or "",
            ]
        ).lower()

        if any(
            term in text
            for term in (
                "recruiter",
                "recruitment",
                "interview",
                "job opportunity",
                "position",
                "hiring",
                "candidate",
            )
        ):
            return "job/recruiter"

        if any(
            term in text
            for term in (
                "assignment",
                "class",
                "course",
                "trainer",
                "student",
                "school",
                "university",
            )
        ):
            return "school/class"

        if any(
            term in text
            for term in (
                "client",
                "website project",
                "project requirements",
                "development project",
                "business website",
            )
        ):
            return "client"

        return "unknown"
