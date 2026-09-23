from integrator.jobs.job_source import JobSource


class TestJobSource(JobSource):

    name = "test"

    def fetch_jobs(self):
        return [
            {
                "title": "SOC Analyst Intern",
                "company": "Demo Security",
                "location": "Remote",
                "application_url": "https://example.com/jobs/soc-analyst",
                "description": (
                    "Entry-level security operations role "
                    "involving monitoring and incident response."
                ),
                "requirements": (
                    "Cybersecurity fundamentals, Linux, networking."
                ),
            },
            {
                "title": "Cybersecurity Analyst Intern",
                "company": "Demo Security",
                "location": "Nairobi, Kenya",
                "application_url": (
                    "https://example.com/jobs/cybersecurity-analyst"
                ),
                "description": (
                    "Support vulnerability management and "
                    "security operations."
                ),
                "requirements": (
                    "Cybersecurity knowledge, Linux and networking."
                ),
            },
            {
                "title": "Cybersecurity Analyst Intern",
                "company": "Demo Security",
                "location": "Nairobi, Kenya",
                "application_url": (
                    "https://example.com/jobs/cybersecurity-analyst"
                ),
                "description": (
                    "Duplicate test listing."
                ),
                "requirements": (
                    "Cybersecurity knowledge."
                ),
            },
        ]
