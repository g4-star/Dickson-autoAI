from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import Email

from integrator.email_engine.models import NormalizedEmail


class EmailRepository:
    """
    Persistence layer for normalized emails.

    Responsibilities:
    - store incoming emails
    - prevent duplicate provider messages
    - retrieve mailbox messages
    - track reply state
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_provider_message_id(
        self,
        *,
        user_id: int,
        provider: str,
        provider_message_id: str,
    ) -> Optional[Email]:
        statement = select(Email).where(
            Email.user_id == user_id,
            Email.provider == provider,
            Email.provider_message_id == provider_message_id,
        )

        return self.db.execute(statement).scalar_one_or_none()

    def save_email(
        self,
        *,
        user_id: int,
        provider: str,
        message: NormalizedEmail,
    ) -> tuple[Email, bool]:
        """
        Save an email if it does not already exist.

        Returns:
            (email, created)

        created=True  -> newly inserted
        created=False -> existing email returned
        """

        existing = self.get_by_provider_message_id(
            user_id=user_id,
            provider=provider,
            provider_message_id=message.provider_message_id,
        )

        if existing:
            return existing, False

        email = Email(
            user_id=user_id,
            provider=provider,
            provider_message_id=message.provider_message_id,
            sender=message.sender,
            recipient=message.recipient,
            subject=message.subject,
            body=message.body,
            thread_id=message.thread_id,
            category=message.category,
            needs_reply=False,
            replied=False,
            received_at=message.received_at,
            created_at=datetime.utcnow(),
        )

        self.db.add(email)
        self.db.commit()
        self.db.refresh(email)

        return email, True

    def list_emails(
        self,
        *,
        user_id: int,
        limit: int = 50,
    ) -> list[Email]:
        statement = (
            select(Email)
            .where(Email.user_id == user_id)
            .order_by(Email.received_at.desc())
            .limit(limit)
        )

        return list(self.db.execute(statement).scalars().all())

    def list_needing_reply(
        self,
        *,
        user_id: int,
        limit: int = 50,
    ) -> list[Email]:
        statement = (
            select(Email)
            .where(
                Email.user_id == user_id,
                Email.needs_reply.is_(True),
                Email.replied.is_(False),
            )
            .order_by(Email.received_at.asc())
            .limit(limit)
        )

        return list(self.db.execute(statement).scalars().all())

    def mark_needs_reply(
        self,
        *,
        email_id: int,
        needs_reply: bool,
    ) -> Optional[Email]:
        email = self.db.get(Email, email_id)

        if email is None:
            return None

        email.needs_reply = needs_reply

        self.db.commit()
        self.db.refresh(email)

        return email

    def mark_replied(
        self,
        *,
        email_id: int,
        reply_body: str,
        reply_status: str = "sent",
    ) -> Optional[Email]:
        email = self.db.get(Email, email_id)

        if email is None:
            return None

        email.replied = True
        email.reply_body = reply_body
        email.reply_status = reply_status
        email.reply_sent_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(email)

        return email
