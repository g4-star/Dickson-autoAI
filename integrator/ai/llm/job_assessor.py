from typing import Any

from integrator.ai.llm.ollama_client import OllamaClient
from integrator.ai.matching.job_analyzer import JobAnalysis
from integrator.ai.profile.candidate_profile import CandidateProfile


class JobAIAssessor:
    """
    Uses the local AI model to interpret an already-verified
    deterministic job analysis.

    The model must never invent candidate qualifications.

    The deterministic JobAnalyzer remains authoritative for
    the fitness score and application threshold.
    """

    def __init__(
        self,
        client: OllamaClient | None = None,
    ):
        self.client = client or OllamaClient()

    def assess(
        self,
        profile: CandidateProfile,
        analysis: JobAnalysis,
    ) -> dict[str, Any]:

        prompt = self._build_prompt(
            profile,
            analysis,
        )

        return self.client.generate_json(prompt)

    def _build_prompt(
        self,
        profile: CandidateProfile,
        analysis: JobAnalysis,
    ) -> str:

        profile_data = profile.to_dict()
        analysis_data = analysis.to_dict()

        return f"""
You are the application-assessment AI for Dickson's autoAI.

Your job is to interpret verified candidate information and a
deterministic job analysis.

The deterministic analyzer has already calculated the fitness score.

STRICT RULES:

1. Never invent qualifications, experience, certifications,
   education, skills, documents, achievements, or work history.

2. NEVER change the fitness score supplied by the deterministic
   analysis.

3. The fitness score is based on required SKILL requirements.

4. Education requirements are informational only and do NOT
   reduce the fitness score.

5. If an education requirement is missing, report it honestly
   as an education gap.

6. Never claim that the candidate has a degree, diploma,
   certification, or qualification that is absent from the
   candidate profile.

7. Missing skills must remain missing.

8. Only use documents that actually exist in the candidate
   profile.

9. If the fitness score is 70 or higher, the decision MUST be
   "APPLY".

10. If the fitness score is below 70, the decision MUST be
    "DO_NOT_APPLY".

11. If a requirement is missing, it must appear in
    "requirements_not_to_claim" when relevant.

12. Do not treat education gaps as missing skills.

13. Do not lower the fitness score because of an education gap.

Return ONLY valid JSON.

Required JSON format:

{{
  "decision": "APPLY",
  "fitness_score": 0,
  "summary": "",
  "matched_skills": [],
  "missing_skills": [],
  "education_gap": "",
  "documents_to_use": [],
  "skills_to_emphasize": [],
  "requirements_not_to_claim": [],
  "application_notes": []
}}

CANDIDATE PROFILE:

{profile_data}

DETERMINISTIC JOB ANALYSIS:

{analysis_data}
"""

if __name__ == "__main__":
    print("JobAIAssessor module loaded successfully.")
