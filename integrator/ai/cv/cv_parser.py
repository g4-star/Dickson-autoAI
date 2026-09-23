import re
from pathlib import Path
from typing import Any


class CVParser:
    """
    Extracts text and structured information from a candidate CV.

    The parser only extracts information that actually exists in the
    supplied document. It must never invent qualifications.
    """

    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".docx",
        ".txt",
    }

    SECTION_ALIASES = {
        "education": [
            "education",
            "academic background",
            "academic qualifications",
        ],
        "experience": [
            "experience",
            "work experience",
            "employment history",
            "professional experience",
        ],
        "skills": [
            "skills",
            "technical skills",
            "core skills",
            "competencies",
        ],
        "certifications": [
            "certifications",
            "certificates",
            "professional certifications",
        ],
        "projects": [
            "projects",
            "personal projects",
            "academic projects",
        ],
        "references": [
            "references",
        ],
    }

    def parse(self, file_path: str) -> dict[str, Any]:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"CV file not found: {file_path}"
            )

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported CV format: {path.suffix}"
            )

        text = self._extract_text(path)

        if not text.strip():
            raise ValueError(
                "CV contains no readable text."
            )

        sections = self._extract_sections(text)

        return {
            "file_name": path.name,
            "file_path": str(path),
            "raw_text": text,
            "sections": sections,
            "skills": self._extract_items(
                sections.get("skills", "")
            ),
            "certifications": self._extract_items(
                sections.get("certifications", "")
            ),
            "education": self._extract_items(
                sections.get("education", "")
            ),
            "experience": self._extract_items(
                sections.get("experience", "")
            ),
            "projects": self._extract_items(
                sections.get("projects", "")
            ),
        }

    def _extract_text(self, path: Path) -> str:
        suffix = path.suffix.lower()

        if suffix == ".txt":
            return path.read_text(
                encoding="utf-8",
                errors="ignore",
            )

        if suffix == ".pdf":
            return self._extract_pdf(path)

        if suffix == ".docx":
            return self._extract_docx(path)

        raise ValueError(
            f"Unsupported file type: {suffix}"
        )

    def _extract_pdf(self, path: Path) -> str:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError(
                "pypdf is required for PDF CV parsing."
            ) from exc

        reader = PdfReader(str(path))

        pages = []

        for page in reader.pages:
            pages.append(page.extract_text() or "")

        return "\n".join(pages)

    def _extract_docx(self, path: Path) -> str:
        try:
            from docx import Document
        except ImportError as exc:
            raise RuntimeError(
                "python-docx is required for DOCX CV parsing."
            ) from exc

        document = Document(str(path))

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n".join(paragraphs)

    def _normalise_heading(self, value: str) -> str:
        value = value.strip().lower()
        value = re.sub(
            r"[^a-z0-9 ]+",
            "",
            value,
        )
        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        for section, aliases in self.SECTION_ALIASES.items():
            if value in aliases:
                return section

        return ""

    def _extract_sections(
        self,
        text: str,
    ) -> dict[str, str]:

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        sections: dict[str, list[str]] = {}
        current_section = "general"

        sections[current_section] = []

        for line in lines:
            heading = self._normalise_heading(line)

            if heading:
                current_section = heading

                if current_section not in sections:
                    sections[current_section] = []

                continue

            sections.setdefault(
                current_section,
                [],
            ).append(line)

        return {
            key: "\n".join(value).strip()
            for key, value in sections.items()
        }

    def _extract_items(self, section_text: str) -> list[str]:
        if not section_text:
            return []

        items = []

        for line in section_text.splitlines():
            line = line.strip()

            if not line:
                continue

            line = re.sub(
                r"^[•*\-–—]\s*",
                "",
                line,
            )

            if line and line not in items:
                items.append(line)

        return items
