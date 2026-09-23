from datetime import datetime, date
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.models import (
    ActivityEvent,
    Application,
    AutomationSettings,
    Email,
    EmailAccount,
    IntegratorStatus,
    Job,
    User,
)
from app.schemas.schemas import (
    ActivityCreate,
    ActivityResponse,
    ApplicationCreate,
    ApplicationResponse,
    ApplicationResponseProcess,
    ApplicationStatusUpdate,
    AutomationSettingsUpdate,
    EmailAccountCreate,
    EmailAccountResponse,
    EmailReplyUpdate,
    EmailResponse,
    IntegratorStatsUpdate,
    JobCreate,
    JobResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)

router = APIRouter(prefix="/api")


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "Dickson's autoAI",
    }


@router.post("/users/{user_id}/cv")
async def upload_cv(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload and store a user's CV.

    Only PDF, DOCX and TXT files are accepted.
    The original filename is never used as the stored filename.
    """

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    allowed_types = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".txt": "text/plain",
    }

    original_name = file.filename or ""
    extension = Path(original_name).suffix.lower()

    if extension not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Unsupported CV format. Please upload PDF, DOCX or TXT.",
        )

    # Read the uploaded file.
    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="The uploaded CV is empty.",
        )

    # Basic size protection: 10 MB maximum.
    max_size = 10 * 1024 * 1024

    if len(contents) > max_size:
        raise HTTPException(
            status_code=400,
            detail="CV is too large. Maximum size is 10 MB.",
        )

    upload_dir = Path("backend/storage/cvs")
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Never trust the user's filename.
    safe_filename = f"user_{user_id}_{uuid4().hex}{extension}"
    destination = upload_dir / safe_filename

    destination.write_bytes(contents)

    # Store a relative path that the integrator can use.
    user.cv_path = str(destination.resolve())

    db.commit()
    db.refresh(user)

    return {
        "message": "CV uploaded successfully",
        "user_id": user.id,
        "cv_path": user.cv_path,
        "filename": original_name,
        "size": len(contents),
    }


# ---------------------------------------------------------
# USERS
# ---------------------------------------------------------

@router.post("/users", response_model=UserResponse)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="User already exists",
        )

    user = User(
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
        location=data.location,
        cv_path=data.cv_path,
        preferred_roles=data.preferred_roles,
        work_preference=data.work_preference,
        salary_preference=data.salary_preference,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    settings = AutomationSettings(
        user_id=user.id
    )

    status = IntegratorStatus(
        user_id=user.id,
        status="offline",
    )

    db.add(settings)
    db.add(status)
    db.commit()

    return user


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user


@router.patch(
    "/users/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    updates = data.model_dump(
        exclude_unset=True
    )

    if "email" in updates:
        existing = (
            db.query(User)
            .filter(
                User.email == updates["email"],
                User.id != user_id,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Email is already in use",
            )

    for key, value in updates.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return user


# ---------------------------------------------------------
# AUTOMATION
# ---------------------------------------------------------

@router.get(
    "/users/{user_id}/automation"
)
def get_automation_settings(
    user_id: int,
    db: Session = Depends(get_db),
):
    settings = (
        db.query(AutomationSettings)
        .filter(
            AutomationSettings.user_id == user_id
        )
        .first()
    )

    if not settings:
        raise HTTPException(
            status_code=404,
            detail="Automation settings not found",
        )

    return settings


@router.patch(
    "/users/{user_id}/automation"
)
def update_automation_settings(
    user_id: int,
    data: AutomationSettingsUpdate,
    db: Session = Depends(get_db),
):
    settings = (
        db.query(AutomationSettings)
        .filter(
            AutomationSettings.user_id == user_id
        )
        .first()
    )

    if not settings:
        raise HTTPException(
            status_code=404,
            detail="Automation settings not found",
        )

    updates = data.model_dump(
        exclude_unset=True
    )

    for key, value in updates.items():
        setattr(settings, key, value)

    db.commit()
    db.refresh(settings)

    return settings


# ---------------------------------------------------------
# JOBS
# ---------------------------------------------------------

@router.post(
    "/users/{user_id}/jobs",
    response_model=JobResponse,
)
def create_job(
    user_id: int,
    data: JobCreate,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    job = Job(
        title=data.title,
        company=data.company,
        location=data.location,
        source=data.source,
        application_url=data.application_url,
        description=data.description,
        requirements=data.requirements,
        status="found",
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


@router.get(
    "/users/{user_id}/jobs",
    response_model=list[JobResponse],
)
def get_jobs(
    user_id: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(Job)
        .order_by(Job.created_at.desc())
        .all()
    )


# ---------------------------------------------------------
# APPLICATIONS
# ---------------------------------------------------------

@router.post(
    "/users/{user_id}/applications",
    response_model=ApplicationResponse,
)
def create_application(
    user_id: int,
    data: ApplicationCreate,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    job = (
        db.query(Job)
        .filter(Job.id == data.job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    existing = (
        db.query(Application)
        .filter(
            Application.user_id == user_id,
            Application.job_id == data.job_id,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Application already exists for this job",
        )

    application = Application(
        user_id=user_id,
        job_id=data.job_id,
        status=data.status,
        cover_letter=data.cover_letter,
        submitted_documents=data.submitted_documents,
        failure_reason=data.failure_reason,
        applied_at=data.applied_at,

        # AI analysis from the integrator.
        fitness_score=data.fitness_score,
        application_decision=data.application_decision,
        matched_requirements=data.matched_requirements,
        missing_requirements=data.missing_requirements,
        preferred_requirements=data.preferred_requirements,
        education_requirements=data.education_requirements,

        # Salary expectation.
        salary_expectation=data.salary_expectation,
        salary_minimum=data.salary_minimum,
        salary_maximum=data.salary_maximum,
        salary_currency=data.salary_currency,
        salary_strategy=data.salary_strategy,
        salary_confidence=data.salary_confidence,

        # Safety record.
        requirements_not_to_claim=data.requirements_not_to_claim,
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return application


@router.patch(
    "/users/{user_id}/applications/{application_id}",
    response_model=ApplicationResponse,
)
def update_application_status(
    user_id: int,
    application_id: int,
    data: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
):
    application = (
        db.query(Application)
        .filter(
            Application.id == application_id,
            Application.user_id == user_id,
        )
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    allowed_statuses = {
        "queued",
        "prepared",
        "submitting",
        "submitted",
        "waiting_for_response",
        "follow_up_pending",
        "success",
        "failed",
        "manual_action_required",
        "stopped",
        "withdrawn",
    }

    if data.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid application status",
        )

    current_status = application.status
    new_status = data.status

    allowed_transitions = {
        "queued": {
            "prepared",
            "failed",
            "manual_action_required",
            "withdrawn",
        },
        "prepared": {
            "submitting",
            "failed",
            "manual_action_required",
            "withdrawn",
        },
        "submitting": {
            "submitted",
            "failed",
            "manual_action_required",
        },
        "submitted": {
            "waiting_for_response",
            "withdrawn",
        },
        "waiting_for_response": {
            "follow_up_pending",
            "success",
            "failed",
            "stopped",
            "manual_action_required",
            "withdrawn",
        },
        "follow_up_pending": {
            "prepared",
            "failed",
            "stopped",
            "withdrawn",
        },
        "success": {
            "withdrawn",
        },
        "failed": {
            "prepared",
            "withdrawn",
        },
        "manual_action_required": {
            "prepared",
            "submitting",
            "failed",
            "withdrawn",
        },
        "stopped": set(),
        "withdrawn": set(),
    }

    if new_status not in allowed_transitions.get(
        current_status,
        set(),
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                f"Invalid application status transition: "
                f"{current_status} -> {new_status}"
            ),
        )

    if new_status == "submitted":
        if data.applied_at is None:
            raise HTTPException(
                status_code=400,
                detail=(
                    "A submitted application requires "
                    "applied_at confirmation."
                ),
            )

        application.applied_at = data.applied_at

    elif data.applied_at is not None:
        application.applied_at = data.applied_at

    application.status = new_status

    if data.failure_reason is not None:
        application.failure_reason = data.failure_reason

    if data.response_category is not None:
        application.response_category = data.response_category
        application.last_response_at = datetime.utcnow()

    if data.next_action_at is not None:
        application.next_action_at = data.next_action_at

    if new_status == "waiting_for_response":
        application.next_action_at = None

    if new_status == "failed" and not application.failure_reason:
        raise HTTPException(
            status_code=400,
            detail="Failed applications require a failure_reason.",
        )

    db.commit()
    db.refresh(application)

    return application


@router.get(
    "/users/{user_id}/applications",
    response_model=list[ApplicationResponse],
)
def get_applications(
    user_id: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(Application)
        .filter(
            Application.user_id == user_id
        )
        .order_by(
            Application.created_at.desc()
        )
        .all()
    )


@router.get(
    "/users/{user_id}/applications/today/count"
)
def applications_today_count(
    user_id: int,
    db: Session = Depends(get_db),
):
    today = date.today()

    applications = (
        db.query(Application)
        .filter(
            Application.user_id == user_id,
            Application.status == "submitted",
            Application.applied_at.isnot(None),
        )
        .all()
    )

    count = 0

    for application in applications:
        if application.applied_at.date() == today:
            count += 1

    return {
        "date": today.isoformat(),
        "count": count,
    }



# ---------------------------------------------------------
# APPLICATION RESPONSE / FOLLOW-UP
# ---------------------------------------------------------

@router.post(
    "/users/{user_id}/applications/{application_id}/response",
    response_model=ApplicationResponse,
)
def process_application_response(
    user_id: int,
    application_id: int,
    data: ApplicationResponseProcess,
    db: Session = Depends(get_db),
):
    application = (
        db.query(Application)
        .filter(
            Application.id == application_id,
            Application.user_id == user_id,
        )
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    if application.status not in {
        "submitted",
        "waiting_for_response",
    }:
        raise HTTPException(
            status_code=409,
            detail=(
                "Application is not waiting for an HR response: "
                f"{application.status}"
            ),
        )

    category = data.response_category

    if not category:
        raise HTTPException(
            status_code=400,
            detail="response_category is required",
        )

    valid_categories = {
        "waiting",
        "interview",
        "success",
        "rejected",
        "follow_up",
        "action_required",
        "stop",
        "manual_review",
    }

    if category not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail="Invalid response_category",
        )

    application.response_category = category
    application.last_response_at = datetime.utcnow()

    if category in {"success", "interview"}:
        application.status = (
            "success"
            if category == "success"
            else "waiting_for_response"
        )

    elif category in {"stop", "rejected"}:
        application.status = (
            "stopped"
            if category == "stop"
            else "failed"
        )

        application.failure_reason = (
            data.failure_reason
            or f"HR response classified as {category}"
        )

    elif category in {"follow_up", "action_required"}:
        if application.attempt_count >= application.max_attempts:
            application.status = "failed"
            application.failure_reason = (
                "Maximum application attempts reached."
            )
            application.next_action_at = None
        else:
            application.status = "follow_up_pending"
            application.next_action_at = (
                data.next_action_at
                or datetime.utcnow()
            )

    else:
        application.status = "waiting_for_response"

    db.commit()
    db.refresh(application)

    return application


# ---------------------------------------------------------
# APPLICATION FOLLOW-UP / REAPPLICATION
# ---------------------------------------------------------

@router.post(
    "/users/{user_id}/applications/{application_id}/follow-up",
    response_model=ApplicationResponse,
)
def start_application_follow_up(
    user_id: int,
    application_id: int,
    db: Session = Depends(get_db),
):
    application = (
        db.query(Application)
        .filter(
            Application.id == application_id,
            Application.user_id == user_id,
        )
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    if application.status != "follow_up_pending":
        raise HTTPException(
            status_code=409,
            detail=(
                "Application is not ready for follow-up: "
                f"{application.status}"
            ),
        )

    if application.attempt_count >= application.max_attempts:
        application.status = "failed"
        application.failure_reason = (
            "Maximum application attempts reached."
        )
        application.next_action_at = None

        db.commit()
        db.refresh(application)

        return application

    application.attempt_count += 1
    application.status = "prepared"
    application.next_action_at = None
    application.response_category = None

    db.commit()
    db.refresh(application)

    return application



# ---------------------------------------------------------
# ACTIVITY
# ---------------------------------------------------------

@router.post(
    "/users/{user_id}/activity",
    response_model=ActivityResponse,
)
def create_activity(
    user_id: int,
    data: ActivityCreate,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    event = ActivityEvent(
        user_id=user_id,
        event_type=data.event_type,
        message=data.message,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


@router.get(
    "/users/{user_id}/activity",
    response_model=list[ActivityResponse],
)
def get_activity(
    user_id: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(ActivityEvent)
        .filter(
            ActivityEvent.user_id == user_id
        )
        .order_by(
            ActivityEvent.created_at.desc()
        )
        .limit(100)
        .all()
    )


# ---------------------------------------------------------
# INTEGRATOR
# ---------------------------------------------------------

@router.get(
    "/users/{user_id}/integrator"
)
def get_integrator_status(
    user_id: int,
    db: Session = Depends(get_db),
):
    status = (
        db.query(IntegratorStatus)
        .filter(
            IntegratorStatus.user_id == user_id
        )
        .first()
    )

    if not status:
        raise HTTPException(
            status_code=404,
            detail="Integrator status not found",
        )

    return status


@router.post(
    "/users/{user_id}/integrator/heartbeat"
)
def integrator_heartbeat(
    user_id: int,
    db: Session = Depends(get_db),
):
    status = (
        db.query(IntegratorStatus)
        .filter(
            IntegratorStatus.user_id == user_id
        )
        .first()
    )

    if not status:
        raise HTTPException(
            status_code=404,
            detail="Integrator status not found",
        )

    status.status = "online"
    status.last_heartbeat = datetime.utcnow()

    db.commit()

    return {
        "status": "online",
        "last_heartbeat": status.last_heartbeat,
    }


@router.patch(
    "/users/{user_id}/integrator/stats"
)
def update_integrator_stats(
    user_id: int,
    data: IntegratorStatsUpdate,
    db: Session = Depends(get_db),
):
    status = (
        db.query(IntegratorStatus)
        .filter(
            IntegratorStatus.user_id == user_id
        )
        .first()
    )

    if not status:
        raise HTTPException(
            status_code=404,
            detail="Integrator status not found",
        )

    updates = data.model_dump(
        exclude_unset=True
    )

    for key, value in updates.items():
        setattr(status, key, value)

    db.commit()
    db.refresh(status)

    return status


# ---------------------------------------------------------
# EMAIL
# ---------------------------------------------------------

@router.post(
    "/users/{user_id}/email-accounts",
    response_model=EmailAccountResponse,
)
def create_email_account(
    user_id: int,
    data: EmailAccountCreate,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    provider = data.provider.strip().lower()
    email_address = str(data.email_address).strip().lower()

    if not provider:
        raise HTTPException(
            status_code=400,
            detail="Email provider is required.",
        )

    supported_providers = {
        "gmail",
        "outlook",
        "imap",
    }

    if provider not in supported_providers:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported email provider. "
                "Supported providers: gmail, outlook, imap."
            ),
        )

    existing = (
        db.query(EmailAccount)
        .filter(
            EmailAccount.user_id == user_id,
            EmailAccount.email_address == email_address,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Email account is already connected.",
        )

    account = EmailAccount(
        user_id=user_id,
        provider=provider,
        email_address=email_address,
        enabled=True,
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return account


@router.get(
    "/users/{user_id}/email-accounts",
    response_model=list[EmailAccountResponse],
)
def get_email_accounts(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return (
        db.query(EmailAccount)
        .filter(
            EmailAccount.user_id == user_id
        )
        .order_by(
            EmailAccount.created_at.desc()
        )
        .all()
    )


@router.get(
    "/users/{user_id}/emails",
    response_model=list[EmailResponse],
)
def get_emails(
    user_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if limit < 1 or limit > 200:
        raise HTTPException(
            status_code=400,
            detail="limit must be between 1 and 200.",
        )

    return (
        db.query(Email)
        .filter(
            Email.user_id == user_id
        )
        .order_by(
            Email.received_at.desc()
        )
        .limit(limit)
        .all()
    )


@router.get(
    "/users/{user_id}/emails/needs-reply",
    response_model=list[EmailResponse],
)
def get_emails_needing_reply(
    user_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if limit < 1 or limit > 200:
        raise HTTPException(
            status_code=400,
            detail="limit must be between 1 and 200.",
        )

    return (
        db.query(Email)
        .filter(
            Email.user_id == user_id,
            Email.needs_reply.is_(True),
            Email.replied.is_(False),
        )
        .order_by(
            Email.received_at.asc()
        )
        .limit(limit)
        .all()
    )


@router.get(
    "/users/{user_id}/emails/{email_id}",
    response_model=EmailResponse,
)
def get_email(
    user_id: int,
    email_id: int,
    db: Session = Depends(get_db),
):
    email = (
        db.query(Email)
        .filter(
            Email.id == email_id,
            Email.user_id == user_id,
        )
        .first()
    )

    if not email:
        raise HTTPException(
            status_code=404,
            detail="Email not found",
        )

    return email


@router.patch(
    "/users/{user_id}/emails/{email_id}/reply",
    response_model=EmailResponse,
)
def update_email_reply(
    user_id: int,
    email_id: int,
    data: EmailReplyUpdate,
    db: Session = Depends(get_db),
):
    email = (
        db.query(Email)
        .filter(
            Email.id == email_id,
            Email.user_id == user_id,
        )
        .first()
    )

    if not email:
        raise HTTPException(
            status_code=404,
            detail="Email not found",
        )

    reply_body = data.reply_body.strip()

    if not reply_body:
        raise HTTPException(
            status_code=400,
            detail="reply_body cannot be empty.",
        )

    # This endpoint records a reply state only.
    # Actual mailbox sending will be implemented later
    # through a legitimate provider integration.
    email.replied = True
    email.reply_body = reply_body
    email.reply_status = "drafted"

    db.commit()
    db.refresh(email)

    return email


@router.post("/users/{user_id}/emails/sync")
def sync_gmail_emails(
    user_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    if limit < 1 or limit > 500:
        raise HTTPException(
            status_code=400,
            detail="limit must be between 1 and 500.",
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    from integrator.email_engine.gmail_provider import GmailProvider
    from integrator.email_engine.engine import EmailEngine
    from integrator.email_engine.sync_service import EmailSyncService

    provider = GmailProvider()
    engine = EmailEngine(provider)

    sync_service = EmailSyncService(
        email_engine=engine,
        db=db,
        provider_name="gmail",
    )

    result = sync_service.sync_user(
        user_id=user_id,
        limit=limit,
    )

    return {
        "status": "ok",
        "fetched": result.fetched,
        "created": result.created,
        "duplicates": result.duplicates,
        "next_page_token": result.next_page_token,
    }
