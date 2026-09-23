from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from app.database.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(200), nullable=False)
    email = Column(String(320), unique=True, nullable=False)
    phone = Column(String(50))
    location = Column(String(200))

    cv_path = Column(String(500))
    preferred_roles = Column(Text)
    work_preference = Column(String(100))
    salary_preference = Column(String(100))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class AutomationSettings(Base):
    __tablename__ = "automation_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)

    job_search = Column(Boolean, default=True)
    auto_apply = Column(Boolean, default=True)
    email_monitoring = Column(Boolean, default=True)
    auto_reply = Column(Boolean, default=False)
    notifications = Column(Boolean, default=True)

    daily_application_target = Column(Integer, default=50)

    require_interview_approval = Column(Boolean, default=True)
    require_offer_approval = Column(Boolean, default=True)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(300), nullable=False)
    company = Column(String(300))
    location = Column(String(300))
    source = Column(String(100))
    application_url = Column(String(1000))

    description = Column(Text)
    requirements = Column(Text)

    match_score = Column(Integer)

    status = Column(String(50), default="found")

    created_at = Column(DateTime, default=datetime.utcnow)


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=False)
    job_id = Column(Integer, nullable=False)

    status = Column(String(50), default="queued")

    cover_letter = Column(Text)
    submitted_documents = Column(Text)

    failure_reason = Column(Text)

    # Reapplication / follow-up lifecycle
    attempt_count = Column(Integer, default=1, nullable=False)
    max_attempts = Column(Integer, default=3, nullable=False)

    response_category = Column(String(100))
    last_response_at = Column(DateTime)
    next_action_at = Column(DateTime)

    applied_at = Column(DateTime)

    # AI application analysis
    fitness_score = Column(Integer)
    application_decision = Column(String(50))

    matched_requirements = Column(Text)
    missing_requirements = Column(Text)
    preferred_requirements = Column(Text)
    education_requirements = Column(Text)

    # Salary expectation
    salary_expectation = Column(Float)
    salary_minimum = Column(Float)
    salary_maximum = Column(Float)
    salary_currency = Column(String(10))
    salary_strategy = Column(String(50))
    salary_confidence = Column(Float)

    # Safety: requirements the candidate must never claim
    requirements_not_to_claim = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)


class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=False, index=True)

    provider = Column(String(50))
    provider_message_id = Column(String(255), index=True)

    sender = Column(String(320))
    recipient = Column(String(320))

    subject = Column(String(500))
    body = Column(Text)

    thread_id = Column(String(255))

    category = Column(String(100))

    needs_reply = Column(Boolean, default=False)
    replied = Column(Boolean, default=False)

    reply_body = Column(Text)
    reply_status = Column(String(50))
    reply_sent_at = Column(DateTime)

    received_at = Column(DateTime)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )


class ActivityEvent(Base):
    __tablename__ = "activity_events"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=False)

    event_type = Column(String(100))
    message = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)


class IntegratorStatus(Base):
    __tablename__ = "integrator_status"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, nullable=False, unique=True)

    status = Column(String(50), default="offline")
    last_heartbeat = Column(DateTime)

    jobs_found_today = Column(Integer, default=0)
    applications_today = Column(Integer, default=0)
    successful_today = Column(Integer, default=0)
    failed_today = Column(Integer, default=0)
    emails_today = Column(Integer, default=0)
    emails_replied_today = Column(Integer, default=0)
    interviews_today = Column(Integer, default=0)


class EmailAccount(Base):
    __tablename__ = "email_accounts"

    id = Column(Integer, primary_key=True, index=True)

    # AutoAI user who owns this mailbox connection
    user_id = Column(Integer, nullable=False, index=True)

    # Provider identifier, e.g. "gmail"
    provider = Column(String(50), nullable=False)

    # Actual mailbox being monitored.
    # This is intentionally separate from users.email.
    email_address = Column(String(320), nullable=False)

    # Whether AutoAI should monitor this account
    enabled = Column(Boolean, default=True, nullable=False)

    # OAuth/provider account identifier when available
    provider_account_id = Column(String(255))

    # Credential reference.
    # Actual OAuth secrets will NOT be stored directly in this table.
    credential_ref = Column(String(255))

    last_sync_at = Column(DateTime)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
