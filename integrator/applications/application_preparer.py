from dataclasses import dataclass, field
from typing import Any

from integrator.ai.matching.application_decision import ApplicationDecision
from integrator.ai.matching.salary_expectation import SalaryExpectation


@dataclass
class ApplicationPackage:
    job_id: int
    candidate_name: str
    candidate_email: str

    cover_letter: str

    submitted_documents: list[str] = field(
        default_factory=list
    )

    answers: dict[str, str] = field(
        default_factory=dict
    )

    fitness_score: int = 0

    salary_expectation: SalaryExpectation | None = None

    requirements_not_to_claim: list[str] = field(
        default_factory=list
    )


class ApplicationPreparer:
    """
    Creates an application package from verified candidate information.

    This component must never invent qualifications, experience,
    certifications, education, salary information, or other
    candidate information.

    The application decision must already permit the application
    before preparation proceeds.
    """

    def prepare(
        self,
        user: dict[str, Any],
        job: dict[str, Any],
        decision: ApplicationDecision,
        salary_expectation: SalaryExpectation | None = None,
    ) -> ApplicationPackage:

        name = (user.get("full_name") or "").strip()
        email = (user.get("email") or "").strip()
        cv_path = user.get("cv_path")

        if not name:
            raise ValueError(
                "Candidate name is missing"
            )

        if not email:
            raise ValueError(
                "Candidate email is missing"
            )

        if not job.get("id"):
            raise ValueError(
                "Job ID is missing"
            )

        if not job.get("title"):
            raise ValueError(
                "Job title is missing"
            )

        if not decision.apply:
            raise ValueError(
                "Application preparation is blocked because "
                f"fitness score {decision.fitness_score}% is below "
                f"the {decision.threshold}% threshold."
            )

        role = job["title"]
        company = (
            job.get("company")
            or "the hiring organization"
        )

        cover_letter = f"""Dear Hiring Team,

I am writing to apply for the {role} position at {company}.

I am interested in this opportunity because it aligns with my current
career interests and the skills supported by my application profile.

Please find my application details and supporting documents attached
where applicable. I would welcome the opportunity to discuss the role
and my suitability for it.

Kind regards,
{name}
{email}
"""

        documents = []

        if cv_path:
            documents.append("CV")

        answers: dict[str, str] = {}

        if salary_expectation is not None:
            answers["salary_expectation"] = (
                self._format_salary_expectation(
                    salary_expectation
                )
            )

        return ApplicationPackage(
            job_id=job["id"],
            candidate_name=name,
            candidate_email=email,
            cover_letter=cover_letter,
            submitted_documents=documents,
            answers=answers,
            fitness_score=decision.fitness_score,
            salary_expectation=salary_expectation,
            requirements_not_to_claim=(
                list(decision.requirements_not_to_claim)
            ),
        )

    @staticmethod
    def _format_salary_expectation(
        salary: SalaryExpectation,
    ) -> str:

        if salary.strategy == "negotiable":
            return "Negotiable"

        if (
            salary.minimum is not None
            and salary.maximum is not None
            and salary.minimum != salary.maximum
        ):
            return (
                f"{salary.minimum:g}-{salary.maximum:g} "
                f"{salary.currency}"
            )

        if salary.value is not None:
            return (
                f"{salary.value:g} "
                f"{salary.currency}"
            )

        return "Negotiable"
