import logging
import time

from integrator.api_client import AutoAIClient
from integrator.config import (
    BACKEND_URL,
    HEARTBEAT_INTERVAL,
    USER_ID,
)
from integrator.jobs.job_engine import JobEngine
from integrator.applications.application_engine import ApplicationEngine
from integrator.applications.application_preparer import ApplicationPreparer
from integrator.ai.matching.job_analyzer import JobAnalyzer
from integrator.ai.matching.application_decision import ApplicationDecisionEngine
from integrator.ai.matching.salary_expectation import SalaryExpectationEngine
from integrator.ai.cv.cv_parser import CVParser
from integrator.ai.profile.candidate_profile import CandidateProfile
from integrator.jobs.source_registry import JobSourceRegistry
from integrator.jobs.ingestion_service import JobIngestionService
from integrator.applications.submission.submission_engine import SubmissionEngine
from integrator.applications.reapplication_engine import ReapplicationEngine


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | INTEGRATOR | %(levelname)s | %(message)s",
)


class Integrator:

    def __init__(self):
        self.client = AutoAIClient(BACKEND_URL)
        self.job_engine = JobEngine()
        self.application_engine = ApplicationEngine()
        self.application_preparer = ApplicationPreparer()
        self.job_analyzer = JobAnalyzer()
        self.application_decision_engine = ApplicationDecisionEngine()
        self.salary_expectation_engine = SalaryExpectationEngine()
        self.job_registry = JobSourceRegistry()
        self.job_ingestion = JobIngestionService(
            self.client,
            self.job_registry,
        )
        self.submission_engine = SubmissionEngine(self.client)
        self.reapplication_engine = ReapplicationEngine(
            self.client,
            self.submission_engine,
        )
        self.running = False

    def check_backend(self):
        try:
            result = self.client.health()
            logging.info("Backend: %s", result)
            return True
        except Exception as exc:
            logging.error("Backend unavailable: %s", exc)
            return False

    def heartbeat(self):
        try:
            result = self.client.heartbeat(USER_ID)
            logging.info("Heartbeat: %s", result)
        except Exception as exc:
            logging.error("Heartbeat failed: %s", exc)

    def activity(self, event_type, message):
        try:
            self.client.create_activity(
                USER_ID,
                {
                    "event_type": event_type,
                    "message": message,
                },
            )
        except Exception as exc:
            logging.error("Activity logging failed: %s", exc)

    def inspect_configuration(self):
        user = self.client.get_user(USER_ID)
        settings = self.client.get_automation_settings(USER_ID)

        logging.info("User: %s", user.get("full_name"))
        logging.info("Email: %s", user.get("email"))
        logging.info("Preferred roles: %s", user.get("preferred_roles"))
        logging.info("CV: %s", user.get("cv_path"))
        logging.info("Job search: %s", settings.get("job_search"))
        logging.info("Auto apply: %s", settings.get("auto_apply"))
        logging.info(
            "Daily target: %s",
            settings.get("daily_application_target"),
        )

        return user, settings

    def _build_candidate_profile(self, user):
        """
        Build a verified CandidateProfile from the user's
        stored information and CV.

        No qualifications are invented here.
        """

        cv_path = user.get("cv_path")

        if not cv_path:
            raise ValueError(
                "Candidate CV is required for fitness analysis"
            )

        parsed = CVParser().parse(cv_path)

        preferred_roles = [
            role.strip()
            for role in (user.get("preferred_roles") or "").split(",")
            if role.strip()
        ]

        work_preference = [
            item.strip()
            for item in (user.get("work_preference") or "").split(",")
            if item.strip()
        ]

        return CandidateProfile.from_parser_result(
            parsed,
            name=user.get("full_name") or "",
            email=user.get("email") or "",
            phone=user.get("phone") or "",
            location=user.get("location") or "",
            preferred_roles=preferred_roles,
            work_preference=work_preference,
            documents=self._available_documents(user),
        )

    def _available_documents(self, user):
        """
        Return only documents that actually exist.

        At this stage the stored CV is the available document.
        The document store can be expanded later with certificates,
        IDs, portfolios, transcripts, and other verified files.
        """

        cv_path = user.get("cv_path")

        if not cv_path:
            return []

        return [cv_path]

    def process_jobs(self, user, settings, profile):
        jobs = self.client.get_jobs(USER_ID)
        applications = self.client.get_applications(USER_ID)

        today_data = self.client.applications_today_count(USER_ID)
        applications_today = today_data["count"]

        logging.info("Jobs available: %d", len(jobs))
        logging.info("Applications today: %d", applications_today)

        suitable_count = 0
        rejected_count = 0
        prepared_count = 0

        for job in jobs:

            # -------------------------------------------------
            # General job discovery score.
            #
            # This is NOT the application fitness score.
            # -------------------------------------------------

            discovery_match = self.job_engine.evaluate(
                job,
                user,
            )

            logging.info(
                "Job discovery: %s | score=%d | suitable=%s",
                job.get("title"),
                discovery_match.score,
                discovery_match.suitable,
            )

            # -------------------------------------------------
            # Authoritative skill/practical fitness analysis.
            #
            # Education is tracked separately and never reduces
            # the fitness score.
            # -------------------------------------------------

            try:
                analysis = self.job_analyzer.analyze(
                    job,
                    profile,
                )

                fitness_decision = (
                    self.application_decision_engine.decide(
                        analysis,
                        available_documents=self._available_documents(
                            user
                        ),
                    )
                )

            except Exception as exc:
                rejected_count += 1

                logging.error(
                    "Job fitness analysis failed for %s: %s",
                    job.get("title"),
                    exc,
                )

                self.activity(
                    "job_analysis_error",
                    f"Fitness analysis failed for "
                    f"{job.get('title')}: {exc}",
                )

                continue

            logging.info(
                "Job fitness: %s | score=%d | apply=%s",
                job.get("title"),
                fitness_decision.fitness_score,
                fitness_decision.apply,
            )

            # -------------------------------------------------
            # HARD 70% GATE
            # -------------------------------------------------

            if not fitness_decision.apply:

                rejected_count += 1

                self.activity(
                    "job_rejected",
                    f"Rejected {job.get('title')} at "
                    f"{job.get('company') or 'Unknown'} "
                    f"(fitness {fitness_decision.fitness_score}/100): "
                    f"{fitness_decision.reason}",
                )

                logging.info(
                    "Application blocked by fitness threshold: "
                    "%s | %s",
                    job.get("title"),
                    fitness_decision.reason,
                )

                continue

            suitable_count += 1

            # -------------------------------------------------
            # Existing application safety checks.
            # -------------------------------------------------

            decision = self.application_engine.can_apply(
                job,
                settings,
                applications_today,
                applications,
            )

            logging.info(
                "Application decision: %s | %s",
                decision.allowed,
                decision.reason,
            )

            if not decision.allowed:

                self.activity(
                    "application_paused",
                    f"Application paused for "
                    f"{job.get('title')}: "
                    f"{decision.reason}",
                )

                continue

            try:
                # -------------------------------------------------
                # Salary expectation
                #
                # Only use salary information explicitly supplied
                # by the job or trusted market data. Never invent
                # an employer salary.
                # -------------------------------------------------

                salary = self.salary_expectation_engine.calculate(
                    job_title=job.get("title") or "",
                    location=job.get("location"),
                    advertised_min=job.get("salary_min"),
                    advertised_max=job.get("salary_max"),
                    advertised_salary=job.get("salary"),
                    currency=job.get("salary_currency") or "KES",
                )

                logging.info(
                    "Salary expectation: %s | value=%s | strategy=%s",
                    job.get("title"),
                    salary.value,
                    salary.strategy,
                )

                # -------------------------------------------------
                # Prepare application from verified analysis.
                # -------------------------------------------------

                package = self.application_preparer.prepare(
                    user,
                    job,
                    fitness_decision,
                    salary_expectation=salary,
                )

                documents = ", ".join(
                    package.submitted_documents
                ) or "None"

                application_data = {
                    "job_id": package.job_id,
                    "status": "prepared",
                    "cover_letter": package.cover_letter,
                    "submitted_documents": documents,

                    # Authoritative AI analysis.
                    "fitness_score": fitness_decision.fitness_score,
                    "application_decision": (
                        "apply"
                        if fitness_decision.apply
                        else "do_not_apply"
                    ),
                    "matched_requirements": (
                        ", ".join(
                            fitness_decision.matched_requirements
                        )
                        or None
                    ),
                    "missing_requirements": (
                        ", ".join(
                            fitness_decision.missing_requirements
                        )
                        or None
                    ),
                    "preferred_requirements": (
                        ", ".join(
                            fitness_decision.preferred_requirements
                        )
                        or None
                    ),
                    "education_requirements": (
                        ", ".join(
                            fitness_decision.education_requirements
                        )
                        or None
                    ),

                    # Salary analysis.
                    "salary_expectation": salary.value,
                    "salary_minimum": salary.minimum,
                    "salary_maximum": salary.maximum,
                    "salary_currency": salary.currency,
                    "salary_strategy": salary.strategy,
                    "salary_confidence": salary.confidence,

                    # Safety record.
                    "requirements_not_to_claim": (
                        ", ".join(
                            fitness_decision.requirements_not_to_claim
                        )
                        or None
                    ),
                }

                application = self.client.create_application(
                    USER_ID,
                    application_data,
                )

                applications.append(application)
                prepared_count += 1

                self.activity(
                    "application_prepared",
                    f"Application prepared for "
                    f"{job.get('title')} at "
                    f"{job.get('company') or 'Unknown'} "
                    f"(fitness {fitness_decision.fitness_score}/100)",
                )

                logging.info(
                    "Application prepared and recorded: %s",
                    job.get("title"),
                )

                submission = self.submission_engine.submit(
                    USER_ID,
                    job,
                    application,
                )

                submission_status = submission.get("status")

                if submission_status == "submitted":
                    applications_today += 1

                    self.activity(
                        "application_submitted",
                        f"Application submitted for "
                        f"{job.get('title')} at "
                        f"{job.get('company') or 'Unknown'}",
                    )

                    logging.info(
                        "Application submitted: %s",
                        job.get("title"),
                    )

                elif submission_status == "manual_action_required":
                    self.activity(
                        "manual_action_required",
                        f"Manual submission required for "
                        f"{job.get('title')} at "
                        f"{job.get('company') or 'Unknown'}",
                    )

                    logging.warning(
                        "Manual action required: %s",
                        job.get("title"),
                    )

                elif submission_status == "failed":
                    self.activity(
                        "application_failed",
                        f"Application submission failed for "
                        f"{job.get('title')}: "
                        f"{submission.get('message')}",
                    )

                    logging.error(
                        "Application submission failed: %s",
                        job.get("title"),
                    )

                else:
                    logging.info(
                        "Submission skipped for %s: %s",
                        job.get("title"),
                        submission.get("message"),
                    )

            except Exception as exc:

                logging.error(
                    "Application preparation failed for %s: %s",
                    job.get("title"),
                    exc,
                )

                self.activity(
                    "application_error",
                    f"Application preparation failed for "
                    f"{job.get('title')}: {exc}",
                )

        return {
            "jobs": len(jobs),
            "suitable": suitable_count,
            "rejected": rejected_count,
            "prepared": prepared_count,
            "applications_today": applications_today,
        }

    def process_reapplications(self, user):
        """
        Process due application follow-ups/reapplications.

        Reapplications intentionally bypass ApplicationEngine.can_apply()
        because an existing application for the same job is expected.
        The ReapplicationEngine and backend enforce the attempt limit.
        """

        applications = self.client.get_applications(USER_ID)
        jobs = self.client.get_jobs(USER_ID)

        jobs_by_id = {
            job.get("id"): job
            for job in jobs
            if job.get("id") is not None
        }

        pending = [
            application
            for application in applications
            if application.get("status") == "follow_up_pending"
        ]

        if not pending:
            logging.info("Reapplications: none pending")
            return {
                "pending": 0,
                "processed": 0,
                "submitted": 0,
                "manual_action_required": 0,
                "failed": 0,
                "not_due": 0,
            }

        logging.info(
            "Reapplications: %d pending",
            len(pending),
        )

        processed = 0
        submitted = 0
        manual_action_required = 0
        failed = 0
        not_due = 0

        for application in pending:
            application_id = application.get("id")
            job_id = application.get("job_id")
            job = jobs_by_id.get(job_id)

            if not job:
                failed += 1

                logging.error(
                    "Reapplication %s has no matching job %s",
                    application_id,
                    job_id,
                )

                self.activity(
                    "reapplication_error",
                    f"Application {application_id} cannot be "
                    f"reapplied because job {job_id} was not found.",
                )

                continue

            try:
                if not self.reapplication_engine.is_due(application):
                    not_due += 1

                    logging.info(
                        "Reapplication not due: application=%s",
                        application_id,
                    )

                    continue

                logging.info(
                    "Processing reapplication: application=%s | "
                    "job=%s | attempt=%s/%s",
                    application_id,
                    job.get("title"),
                    application.get("attempt_count"),
                    application.get("max_attempts"),
                )

                result = self.reapplication_engine.process(
                    USER_ID,
                    application,
                    job,
                    user,
                )

                processed += 1

                result_status = result.get("status")

                if result_status == "submitted":
                    submitted += 1

                    self.activity(
                        "reapplication_submitted",
                        f"Reapplication submitted for "
                        f"{job.get('title')} at "
                        f"{job.get('company') or 'Unknown'} "
                        f"(application {application_id})",
                    )

                    logging.info(
                        "Reapplication submitted: %s",
                        job.get("title"),
                    )

                elif result_status == "manual_action_required":
                    manual_action_required += 1

                    self.activity(
                        "reapplication_manual_action_required",
                        f"Manual action required for reapplication "
                        f"of {job.get('title')} at "
                        f"{job.get('company') or 'Unknown'}",
                    )

                    logging.warning(
                        "Reapplication requires manual action: %s",
                        job.get("title"),
                    )

                elif result_status == "failed":
                    failed += 1

                    self.activity(
                        "reapplication_failed",
                        f"Reapplication failed for "
                        f"{job.get('title')}: "
                        f"{result.get('message')}",
                    )

                    logging.error(
                        "Reapplication failed: %s | %s",
                        job.get("title"),
                        result.get("message"),
                    )

                elif result_status == "not_due":
                    not_due += 1
                    processed -= 1

                else:
                    logging.info(
                        "Reapplication result for %s: %s",
                        job.get("title"),
                        result,
                    )

            except Exception as exc:
                failed += 1

                logging.exception(
                    "Reapplication processing failed for "
                    "application %s: %s",
                    application_id,
                    exc,
                )

                self.activity(
                    "reapplication_error",
                    f"Reapplication failed for application "
                    f"{application_id}: {exc}",
                )

        return {
            "pending": len(pending),
            "processed": processed,
            "submitted": submitted,
            "manual_action_required": manual_action_required,
            "failed": failed,
            "not_due": not_due,
        }

    def run_once(self):

        logging.info("Starting integrator cycle")

        if not self.check_backend():
            return

        self.heartbeat()

        try:
            user, settings = self.inspect_configuration()

            if settings.get("job_search"):
                ingestion = self.job_ingestion.ingest(USER_ID)

                logging.info(
                    "Job ingestion | raw=%d | normalized=%d | "
                    "unique=%d | created=%d | skipped=%d",
                    ingestion["raw"],
                    ingestion["normalized"],
                    ingestion["unique"],
                    ingestion["created"],
                    ingestion["skipped"],
                )

                self.activity(
                    "job_ingestion",
                    f"Fetched {ingestion['raw']} jobs; "
                    f"stored {ingestion['created']} new jobs; "
                    f"skipped {ingestion['skipped']} duplicates",
                )

            if not settings.get("job_search"):
                logging.info("Job search is disabled")
                return

            try:
                profile = self._build_candidate_profile(user)
            except Exception as exc:
                logging.error(
                    "Candidate profile unavailable: %s",
                    exc,
                )

                self.activity(
                    "profile_error",
                    f"Candidate profile unavailable: {exc}",
                )

                return

            result = self.process_jobs(
                user,
                settings,
                profile,
            )

            reapplications = self.process_reapplications(
                user,
            )

            logging.info(
                "Cycle complete | jobs=%d | suitable=%d | "
                "rejected=%d | prepared=%d | submitted_today=%d | "
                "reapplications=%d | reapplied=%d | "
                "manual=%d | reapplication_failed=%d",
                result["jobs"],
                result["suitable"],
                result["rejected"],
                result["prepared"],
                result["applications_today"],
                reapplications["pending"],
                reapplications["submitted"],
                reapplications["manual_action_required"],
                reapplications["failed"],
            )

        except Exception as exc:

            logging.exception(
                "Integrator cycle failed: %s",
                exc,
            )

            self.activity(
                "integrator_error",
                str(exc),
            )

    def run(self):

        self.running = True

        logging.info(
            "Dickson's autoAI Integrator started"
        )

        while self.running:

            self.run_once()

            logging.info(
                "Sleeping for %d seconds",
                HEARTBEAT_INTERVAL,
            )

            time.sleep(HEARTBEAT_INTERVAL)


if __name__ == "__main__":
    Integrator().run()
