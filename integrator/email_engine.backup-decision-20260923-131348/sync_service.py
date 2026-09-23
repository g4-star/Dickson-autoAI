from dataclasses import dataclass

from sqlalchemy.orm import Session

from integrator.email_engine.classifier import EmailClassifier
from integrator.email_engine.engine import EmailEngine
from integrator.email_engine.repository import EmailRepository


@dataclass
class EmailSyncResult:
    fetched: int
    created: int
    duplicates: int


class EmailSyncService:
    """
    Coordinates mailbox fetching, classification, and persistence.

    Flow:

        EmailProvider
            ↓
        EmailEngine
            ↓
        NormalizedEmail
            ↓
        EmailClassifier
            ↓
        EmailRepository
            ↓
        Database
    """

    def __init__(
        self,
        *,
        email_engine: EmailEngine,
        db: Session,
        provider_name: str,
        classifier: EmailClassifier | None = None,
    ):
        self.email_engine = email_engine
        self.repository = EmailRepository(db)
        self.provider_name = provider_name
        self.classifier = classifier or EmailClassifier()

    def sync_user(
        self,
        *,
        user_id: int,
        limit: int = 50,
    ) -> EmailSyncResult:
        messages = self.email_engine.fetch_recent(
            limit=limit,
        )

        created = 0
        duplicates = 0

        for message in messages:
            existing = self.repository.get_by_provider_message_id(
                user_id=user_id,
                provider=self.provider_name,
                provider_message_id=message.provider_message_id,
            )

            if existing:
                duplicates += 1
                continue

            classification = self.classifier.classify(message)

            message.category = classification.category

            email, was_created = self.repository.save_email(
                user_id=user_id,
                provider=self.provider_name,
                message=message,
            )

            if was_created:
                email.needs_reply = classification.needs_reply

                self.repository.db.commit()
                self.repository.db.refresh(email)

                created += 1
            else:
                duplicates += 1

        return EmailSyncResult(
            fetched=len(messages),
            created=created,
            duplicates=duplicates,
        )
