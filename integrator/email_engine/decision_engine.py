from dataclasses import dataclass
from enum import Enum

from integrator.email_engine.classifier import EmailClassification
from integrator.email_engine.models import NormalizedEmail


class ReplyDecision(str, Enum):
    AUTO_REPLY = "auto_reply"
    DRAFT_FOR_REVIEW = "draft_for_review"
    NO_REPLY = "no_reply"


@dataclass
class EmailDecision:
    decision: ReplyDecision
    confidence: float
    reason: str


class EmailDecisionEngine:
    """
    Conservative decision layer for incoming emails.

    Classification answers:
        "What kind of email is this?"

    Decision answers:
        "What should autoAI do with it?"

    This engine does NOT send emails.
    """

    def decide(
        self,
        message: NormalizedEmail,
        classification: EmailClassification,
    ) -> EmailDecision:

        # Automated messages must never trigger a reply.
        if classification.category in {
            "newsletter",
            "service/notification",
            "spam/irrelevant",
        }:
            return EmailDecision(
                decision=ReplyDecision.NO_REPLY,
                confidence=0.99,
                reason=(
                    "Automated, informational, or unwanted "
                    "message. No reply required."
                ),
            )

        # Unknown messages should never be auto-replied to.
        if classification.category == "personal/professional":
            return EmailDecision(
                decision=ReplyDecision.DRAFT_FOR_REVIEW,
                confidence=0.70,
                reason=(
                    "Message may require a response, but its "
                    "intent is not sufficiently clear for automatic sending."
                ),
            )

        # A classified message that does not require a reply
        # should remain untouched.
        if not classification.needs_reply:
            return EmailDecision(
                decision=ReplyDecision.NO_REPLY,
                confidence=0.95,
                reason="Classifier determined that no reply is required.",
            )

        # School and client messages can usually be prepared
        # for automatic handling, provided the classifier is confident.
        if classification.category in {
            "school/class",
            "client",
        }:
            if classification.confidence >= 0.85:
                return EmailDecision(
                    decision=ReplyDecision.AUTO_REPLY,
                    confidence=0.90,
                    reason=(
                        "High-confidence school or client communication "
                        "requiring a response."
                    ),
                )

            return EmailDecision(
                decision=ReplyDecision.DRAFT_FOR_REVIEW,
                confidence=0.75,
                reason=(
                    "Potentially actionable message, but classification "
                    "confidence is not high enough for automatic reply."
                ),
            )

        # Recruiter messages require additional caution.
        #
        # We can safely identify them as requiring attention, but
        # interview invitations, offers, salary discussions, etc.
        # should initially be reviewed before sending.
        if classification.category == "job/recruiter":
            subject = (message.subject or "").lower()
            body = (message.body or "").lower()

            sensitive_recruitment_terms = (
                "interview",
                "salary",
                "compensation",
                "offer",
                "employment contract",
                "start date",
                "availability",
                "relocation",
                "assessment",
                "technical test",
                "background check",
                "reference",
            )

            if any(
                term in subject or term in body
                for term in sensitive_recruitment_terms
            ):
                return EmailDecision(
                    decision=ReplyDecision.DRAFT_FOR_REVIEW,
                    confidence=0.92,
                    reason=(
                        "Recruitment message contains a sensitive or "
                        "decision-relevant topic and requires review."
                    ),
                )

            if classification.confidence >= 0.90:
                return EmailDecision(
                    decision=ReplyDecision.AUTO_REPLY,
                    confidence=0.88,
                    reason=(
                        "High-confidence recruitment communication "
                        "without sensitive decision-making content."
                    ),
                )

            return EmailDecision(
                decision=ReplyDecision.DRAFT_FOR_REVIEW,
                confidence=0.75,
                reason=(
                    "Recruitment message detected, but confidence "
                    "is insufficient for automatic sending."
                ),
            )

        # Safe default.
        return EmailDecision(
            decision=ReplyDecision.DRAFT_FOR_REVIEW,
            confidence=0.60,
            reason="No automatic reply rule matched.",
        )
