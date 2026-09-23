from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    cv_path: Optional[str] = None
    preferred_roles: Optional[str] = None
    work_preference: Optional[str] = None
    salary_preference: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    cv_path: Optional[str] = None
    preferred_roles: Optional[str] = None
    work_preference: Optional[str] = None
    salary_preference: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    cv_path: Optional[str] = None
    preferred_roles: Optional[str] = None
    work_preference: Optional[str] = None
    salary_preference: Optional[str] = None

    class Config:
        from_attributes = True


class AutomationSettingsUpdate(BaseModel):
    job_search: Optional[bool] = None
    auto_apply: Optional[bool] = None
    email_monitoring: Optional[bool] = None
    auto_reply: Optional[bool] = None
    notifications: Optional[bool] = None

    daily_application_target: Optional[int] = None

    require_interview_approval: Optional[bool] = None
    require_offer_approval: Optional[bool] = None


class JobCreate(BaseModel):
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    source: Optional[str] = None
    application_url: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None


class JobResponse(BaseModel):
    id: int
    title: str
    company: Optional[str]
    location: Optional[str]
    source: Optional[str]
    application_url: Optional[str]
    description: Optional[str]
    requirements: Optional[str]
    match_score: Optional[int]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ApplicationCreate(BaseModel):
    job_id: int
    status: str = "queued"
    cover_letter: Optional[str] = None
    submitted_documents: Optional[str] = None
    failure_reason: Optional[str] = None
    applied_at: Optional[datetime] = None

    # AI analysis produced by the integrator.
    # These fields are optional so normal application creation
    # remains backward-compatible.
    fitness_score: Optional[int] = None
    application_decision: Optional[str] = None

    matched_requirements: Optional[str] = None
    missing_requirements: Optional[str] = None
    preferred_requirements: Optional[str] = None
    education_requirements: Optional[str] = None

    # Salary expectation produced by the salary engine.
    salary_expectation: Optional[float] = None
    salary_minimum: Optional[float] = None
    salary_maximum: Optional[float] = None
    salary_currency: Optional[str] = None
    salary_strategy: Optional[str] = None
    salary_confidence: Optional[float] = None

    requirements_not_to_claim: Optional[str] = None


class ApplicationStatusUpdate(BaseModel):
    status: str
    failure_reason: Optional[str] = None
    applied_at: Optional[datetime] = None
    response_category: Optional[str] = None
    next_action_at: Optional[datetime] = None


class ApplicationResponseProcess(BaseModel):
    response_category: str
    failure_reason: Optional[str] = None
    next_action_at: Optional[datetime] = None


class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    job_id: int
    status: str
    cover_letter: Optional[str]
    submitted_documents: Optional[str]
    failure_reason: Optional[str]

    attempt_count: int
    max_attempts: int

    response_category: Optional[str]
    last_response_at: Optional[datetime]
    next_action_at: Optional[datetime]

    applied_at: Optional[datetime]
    created_at: datetime

    # AI application analysis
    fitness_score: Optional[int]
    application_decision: Optional[str]

    matched_requirements: Optional[str]
    missing_requirements: Optional[str]
    preferred_requirements: Optional[str]
    education_requirements: Optional[str]

    # Salary expectation
    salary_expectation: Optional[float]
    salary_minimum: Optional[float]
    salary_maximum: Optional[float]
    salary_currency: Optional[str]
    salary_strategy: Optional[str]
    salary_confidence: Optional[float]

    requirements_not_to_claim: Optional[str]

    class Config:
        from_attributes = True


class ActivityCreate(BaseModel):
    event_type: str
    message: str


class ActivityResponse(BaseModel):
    id: int
    event_type: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


class IntegratorStatsUpdate(BaseModel):
    jobs_found_today: Optional[int] = None
    applications_today: Optional[int] = None
    successful_today: Optional[int] = None
    failed_today: Optional[int] = None
    emails_today: Optional[int] = None
    emails_replied_today: Optional[int] = None
    interviews_today: Optional[int] = None


class EmailAccountCreate(BaseModel):
    provider: str
    email_address: EmailStr


class EmailAccountResponse(BaseModel):
    id: int
    user_id: int
    provider: str
    email_address: EmailStr
    enabled: bool
    provider_account_id: Optional[str]
    last_sync_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmailResponse(BaseModel):
    id: int
    user_id: int
    provider: Optional[str]
    provider_message_id: Optional[str]
    sender: Optional[EmailStr]
    recipient: Optional[EmailStr]
    subject: Optional[str]
    body: Optional[str]
    thread_id: Optional[str]
    category: Optional[str]

    needs_reply: bool
    replied: bool
    reply_body: Optional[str]
    reply_status: Optional[str]
    reply_sent_at: Optional[datetime]

    received_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class EmailReplyUpdate(BaseModel):
    reply_body: str
