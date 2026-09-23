from dataclasses import dataclass, field
import re
from typing import List, Tuple


@dataclass
class RequirementMatch:
    requirement: str
    matched: bool
    evidence: List[str] = field(default_factory=list)


@dataclass
class JobAnalysis:
    matched_requirements: List[RequirementMatch]
    missing_requirements: List[RequirementMatch]
    preferred_requirements: List[RequirementMatch]
    education_requirements: List[RequirementMatch]

    score: int
    suitable: bool
    reasons: List[str] = field(default_factory=list)

    @property
    def matched(self):
        return self.matched_requirements

    @property
    def missing(self):
        return self.missing_requirements

    @property
    def preferred(self):
        return self.preferred_requirements


class JobAnalyzer:
    """
    Analyzes a job against a CandidateProfile.

    Important rules:
    - Fitness measures practical skill alignment.
    - Preferred/nice-to-have skills do NOT reduce fitness.
    - Education requirements are tracked separately.
    - Missing requirements are never treated as candidate skills.
    - No qualifications are invented.
    """

    FITNESS_THRESHOLD = 70

    SKILL_ALIASES = {
        "linux": (
            "linux",
            "linux administration",
            "linux systems",
        ),
        "python": (
            "python",
            "python programming",
        ),
        "networking": (
            "networking",
            "computer networking",
            "network administration",
        ),
        "cybersecurity": (
            "cybersecurity",
            "cyber security",
            "information security",
            "infosec",
        ),
        "flutter": (
            "flutter",
            "flutter development",
        ),
        "react": (
            "react",
            "reactjs",
            "react.js",
        ),
        "sql": (
            "sql",
            "structured query language",
        ),
        "siem": (
            "siem",
            "security information and event management",
        ),
        "penetration testing": (
            "penetration testing",
            "penetration test",
            "pentesting",
            "pen testing",
        ),
        "aws": (
            "aws",
            "amazon web services",
        ),
        "kubernetes": (
            "kubernetes",
            "k8s",
        ),
        "java": (
            "java",
            "java programming",
        ),
    }

    PREFERRED_PATTERNS = (
        "preferred",
        "nice to have",
        "nice-to-have",
        "bonus",
        "plus",
        "desired",
        "optional",
    )

    REQUIRED_SECTION_PATTERNS = (
        "required",
        "requirements",
        "must have",
        "must-have",
        "essential",
        "qualifications",
    )

    PREFERRED_SECTION_PATTERNS = (
        "preferred",
        "nice to have",
        "nice-to-have",
        "desired",
        "bonus",
        "optional",
        "plus",
    )

    EDUCATION_PATTERNS = (
        "bachelor",
        "bachelor's",
        "master",
        "master's",
        "degree",
        "diploma",
        "phd",
        "doctorate",
        "certification",
        "certified",
    )

    def analyze(self, job, candidate_profile) -> JobAnalysis:
        text = self._combined_job_text(job)

        requirements = self._extract_requirements(text)

        matched = []
        missing = []
        preferred = []

        for requirement, required in requirements:
            result = self._match_requirement(
                requirement,
                candidate_profile,
            )

            if required:
                if result.matched:
                    matched.append(result)
                else:
                    missing.append(result)
            else:
                preferred.append(result)

        education = self._extract_education_requirements(text)

        score = self._calculate_score(
            matched_count=len(matched),
            required_count=len(matched) + len(missing),
        )

        suitable = score >= self.FITNESS_THRESHOLD

        reasons = []

        if missing:
            reasons.append(
                f"{len(missing)} required skill requirement(s) were not found."
            )

        required_count = len(matched) + len(missing)

        if required_count:
            reasons.append(
                f"{len(matched)} of {required_count} required skill "
                f"requirements are supported."
            )
        else:
            reasons.append(
                "No required skill requirements were identified."
            )

        if preferred:
            preferred_matched = sum(
                1 for item in preferred if item.matched
            )

            reasons.append(
                f"Preferred skills: {preferred_matched} of "
                f"{len(preferred)} supported; preferred skills do not "
                f"reduce fitness."
            )

        if education:
            education_matched = sum(
                1 for item in education if item.matched
            )

            reasons.append(
                f"Education requirements: {education_matched} of "
                f"{len(education)} supported; education does not affect fitness."
            )

        if suitable:
            reasons.append(
                f"Fitness meets the {self.FITNESS_THRESHOLD}% "
                "application threshold."
            )
        else:
            reasons.append(
                f"Fitness is below the {self.FITNESS_THRESHOLD}% "
                "application threshold."
            )

        return JobAnalysis(
            matched_requirements=matched,
            missing_requirements=missing,
            preferred_requirements=preferred,
            education_requirements=education,
            score=score,
            suitable=suitable,
            reasons=reasons,
        )

    def _combined_job_text(self, job) -> str:
        description = job.get("description") or ""
        requirements = job.get("requirements") or ""

        return f"""
{description}

{requirements}
""".strip()

    def _extract_requirements(
        self,
        text: str,
    ) -> List[Tuple[str, bool]]:
        """
        Return:
            [(canonical_skill, required), ...]

        Section context is respected.

        Example:

        Required:
        Linux
        Python

        Preferred:
        SIEM
        AWS

        becomes:

        linux -> required
        python -> required
        siem -> preferred
        aws -> preferred
        """

        requirements = []

        current_section = "required"

        for raw_line in text.splitlines():
            line = raw_line.strip()

            if not line:
                continue

            line_lower = line.lower()

            # Detect section headings.
            if self._is_section(line_lower, self.PREFERRED_SECTION_PATTERNS):
                current_section = "preferred"
                continue

            if self._is_section(line_lower, self.REQUIRED_SECTION_PATTERNS):
                current_section = "required"
                continue

            # Ignore obvious headings that are not skill requirements.
            if line.endswith(":"):
                continue

            for canonical, aliases in self.SKILL_ALIASES.items():
                if not self._contains_alias(line_lower, aliases):
                    continue

                explicit_preferred = any(
                    pattern in line_lower
                    for pattern in self.PREFERRED_PATTERNS
                )

                is_preferred = (
                    current_section == "preferred"
                    or explicit_preferred
                )

                requirements.append(
                    (canonical, not is_preferred)
                )

        # Merge duplicates.
        # If a skill appears once as required and once as preferred,
        # required wins.
        merged = {}

        for requirement, required in requirements:
            if requirement not in merged:
                merged[requirement] = required
            else:
                merged[requirement] = (
                    merged[requirement] or required
                )

        return list(merged.items())

    def _is_section(
        self,
        line_lower: str,
        patterns: Tuple[str, ...],
    ) -> bool:
        """
        Detect requirement section headings.

        Supports headings such as:
        - Required:
        - Required skills:
        - Required qualifications:
        - Preferred:
        - Preferred skills:
        - Nice to have:
        - Desired qualifications:

        Only treat a line as a section heading when the pattern
        appears at the beginning and the remainder is a known
        heading qualifier.
        """
        normalized = line_lower.strip(" :-")
        normalized = re.sub(r"\\s+", " ", normalized)

        heading_qualifiers = (
            "",
            "skills",
            "skill",
            "requirements",
            "requirement",
            "qualifications",
            "qualification",
            "experience",
            "experience requirements",
            "skills and experience",
        )

        for pattern in patterns:
            pattern = pattern.lower().strip()

            if normalized == pattern:
                return True

            if not normalized.startswith(pattern + " "):
                continue

            remainder = normalized[len(pattern):].strip(" :-")

            if remainder in heading_qualifiers:
                return True

        return False

    def _contains_alias(
        self,
        text: str,
        aliases: Tuple[str, ...],
    ) -> bool:
        for alias in aliases:
            escaped = re.escape(alias.lower())

            if re.search(
                rf"(?<![a-z0-9]){escaped}(?![a-z0-9])",
                text,
            ):
                return True

        return False

    def _match_requirement(
        self,
        requirement: str,
        candidate_profile,
    ) -> RequirementMatch:
        candidate_text = self._candidate_text(candidate_profile).lower()

        aliases = self.SKILL_ALIASES.get(
            requirement,
            (requirement,),
        )

        evidence = []

        for alias in aliases:
            if self._contains_alias(candidate_text, (alias,)):
                evidence.append(alias)

        return RequirementMatch(
            requirement=requirement,
            matched=bool(evidence),
            evidence=evidence,
        )

    def _candidate_text(self, candidate_profile) -> str:
        parts = []

        for attribute in (
            "skills",
            "certifications",
            "education",
            "experience",
            "projects",
            "preferred_roles",
            "work_preference",
            "documents",
        ):
            value = getattr(candidate_profile, attribute, None)

            if not value:
                continue

            if isinstance(value, list):
                parts.extend(str(item) for item in value)
            else:
                parts.append(str(value))

        return " ".join(parts)

    def _extract_education_requirements(
        self,
        text: str,
    ) -> List[RequirementMatch]:
        results = []
        seen = set()

        for raw_line in text.splitlines():
            line = raw_line.strip()

            if not line:
                continue

            lower = line.lower()

            if not any(
                pattern in lower
                for pattern in self.EDUCATION_PATTERNS
            ):
                continue

            normalized = re.sub(
                r"[^a-z0-9 ]+",
                " ",
                lower,
            )

            normalized = re.sub(
                r"\s+",
                " ",
                normalized,
            ).strip()

            if normalized in seen:
                continue

            seen.add(normalized)

            results.append(
                RequirementMatch(
                    requirement=line,
                    matched=False,
                    evidence=[],
                )
            )

        return results

    def _calculate_score(
        self,
        matched_count: int,
        required_count: int,
    ) -> int:
        if required_count == 0:
            return 100

        return round(
            (matched_count / required_count) * 100
        )
