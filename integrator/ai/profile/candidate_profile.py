from dataclasses import dataclass, field, asdict
from typing import Any
import json


@dataclass
class CandidateIdentity:
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""


@dataclass
class CandidateProfile:
    """
    Structured representation of verified candidate information.

    This profile must contain only information extracted from the
    candidate's supplied CV, documents, or explicitly provided settings.
    It must never invent qualifications or experience.
    """

    identity: CandidateIdentity = field(
        default_factory=CandidateIdentity
    )

    education: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    experience: list[str] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)

    preferred_roles: list[str] = field(default_factory=list)
    work_preference: list[str] = field(default_factory=list)

    documents: list[str] = field(default_factory=list)

    source_cv: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            indent=2,
            ensure_ascii=False,
        )

    @classmethod
    def from_parser_result(
        cls,
        parsed: dict[str, Any],
        *,
        name: str = "",
        email: str = "",
        phone: str = "",
        location: str = "",
        preferred_roles: list[str] | None = None,
        work_preference: list[str] | None = None,
        documents: list[str] | None = None,
    ) -> "CandidateProfile":
        return cls(
            identity=CandidateIdentity(
                name=name,
                email=email,
                phone=phone,
                location=location,
            ),
            education=parsed.get("education", []),
            certifications=parsed.get("certifications", []),
            skills=parsed.get("skills", []),
            experience=parsed.get("experience", []),
            projects=parsed.get("projects", []),
            preferred_roles=preferred_roles or [],
            work_preference=work_preference or [],
            documents=documents or [],
            source_cv=parsed.get("file_path"),
        )
