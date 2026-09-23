from dataclasses import dataclass, field, asdict
from typing import Any

from integrator.ai.matching.job_analyzer import JobAnalysis


FITNESS_THRESHOLD = 70


@dataclass
class ApplicationDecision:
    fitness_score: int
    threshold: int

    apply: bool

    matched_requirements: list[str] = field(default_factory=list)
    missing_requirements: list[str] = field(default_factory=list)

    preferred_requirements: list[str] = field(default_factory=list)
    education_requirements: list[str] = field(default_factory=list)

    documents_to_submit: list[str] = field(default_factory=list)

    # Requirements that AutoAI must never claim the candidate has.
    requirements_not_to_claim: list[str] = field(
        default_factory=list
    )

    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ApplicationDecisionEngine:
    """
    Enforces the AutoAI application threshold.

    Fitness is based on supported skill requirements only.

    Education requirements are tracked separately and NEVER
    reduce the fitness score.

    Salary does not affect fitness.

    Missing skills or qualifications are never fabricated.
    """

    def __init__(
        self,
        threshold: int = FITNESS_THRESHOLD,
    ):
        if not 0 <= threshold <= 100:
            raise ValueError(
                "Fitness threshold must be between 0 and 100."
            )

        self.threshold = threshold

    def decide(
        self,
        analysis: JobAnalysis,
        available_documents: list[str] | None = None,
    ) -> ApplicationDecision:

        documents = list(available_documents or [])

        apply = analysis.score >= self.threshold

        matched = [
            item.requirement
            for item in analysis.matched_requirements
        ]

        missing = [
            item.requirement
            for item in analysis.missing_requirements
        ]

        preferred = [
            item.requirement
            for item in analysis.preferred_requirements
        ]

        education = [
            item.requirement
            for item in analysis.education_requirements
        ]

        if apply:
            reason = (
                f"Fitness score {analysis.score}% meets the "
                f"{self.threshold}% application threshold."
            )
        else:
            reason = (
                f"Fitness score {analysis.score}% is below the "
                f"{self.threshold}% application threshold. "
                "Application will not be submitted."
            )

        if education:
            reason += (
                " Education requirements were evaluated separately "
                "and did not affect fitness."
            )

        return ApplicationDecision(
            fitness_score=analysis.score,
            threshold=self.threshold,
            apply=apply,
            matched_requirements=matched,
            missing_requirements=missing,
            preferred_requirements=preferred,
            education_requirements=education,
            documents_to_submit=documents,
            requirements_not_to_claim=missing,
            reason=reason,
        )
