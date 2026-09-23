from dataclasses import dataclass
from typing import Optional


@dataclass
class SalaryExpectation:
    value: Optional[float]
    minimum: Optional[float]
    maximum: Optional[float]
    currency: str
    strategy: str
    confidence: float
    reason: str


class SalaryExpectationEngine:
    """
    Determines a reasonable salary expectation for a job application.

    Rules:
    1. Never invent an employer-provided salary.
    2. Prefer the employer's advertised range.
    3. Use a fixed advertised salary when one is explicitly given.
    4. Use a market-based estimate only when reliable market data
       is supplied.
    5. Fall back to "negotiable" when there is insufficient evidence.
    """

    def calculate(
        self,
        *,
        job_title: str,
        location: Optional[str] = None,
        seniority: Optional[str] = None,
        advertised_min: Optional[float] = None,
        advertised_max: Optional[float] = None,
        advertised_salary: Optional[float] = None,
        currency: str = "KES",
        market_min: Optional[float] = None,
        market_max: Optional[float] = None,
    ) -> SalaryExpectation:

        currency = currency.upper()

        # ---------------------------------------------------------
        # 1. Explicit employer salary range
        # ---------------------------------------------------------
        if advertised_min is not None and advertised_max is not None:
            if advertised_min > advertised_max:
                raise ValueError(
                    "advertised_min cannot be greater than advertised_max"
                )

            midpoint = (advertised_min + advertised_max) / 2

            return SalaryExpectation(
                value=round(midpoint, 2),
                minimum=advertised_min,
                maximum=advertised_max,
                currency=currency,
                strategy="advertised_range",
                confidence=0.98,
                reason=(
                    "Employer provided a salary range. "
                    "Expectation is based on the advertised range."
                ),
            )

        # ---------------------------------------------------------
        # 2. Explicit fixed employer salary
        # ---------------------------------------------------------
        if advertised_salary is not None:
            return SalaryExpectation(
                value=advertised_salary,
                minimum=advertised_salary,
                maximum=advertised_salary,
                currency=currency,
                strategy="advertised_salary",
                confidence=0.99,
                reason=(
                    "Employer provided an explicit salary amount."
                ),
            )

        # ---------------------------------------------------------
        # 3. Reliable market range
        # ---------------------------------------------------------
        if market_min is not None and market_max is not None:
            if market_min > market_max:
                raise ValueError(
                    "market_min cannot be greater than market_max"
                )

            midpoint = (market_min + market_max) / 2

            return SalaryExpectation(
                value=round(midpoint, 2),
                minimum=market_min,
                maximum=market_max,
                currency=currency,
                strategy="market_range",
                confidence=0.80,
                reason=(
                    f"No employer salary was provided for "
                    f"{job_title}. A market range was supplied "
                    f"for comparison."
                ),
            )

        # ---------------------------------------------------------
        # 4. Insufficient evidence
        # ---------------------------------------------------------
        return SalaryExpectation(
            value=None,
            minimum=None,
            maximum=None,
            currency=currency,
            strategy="negotiable",
            confidence=0.95,
            reason=(
                "There is insufficient reliable salary information "
                "to calculate a defensible numeric expectation."
            ),
        )
