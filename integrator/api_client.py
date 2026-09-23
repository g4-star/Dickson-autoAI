import requests


class AutoAIClient:
    def __init__(
        self,
        base_url="http://127.0.0.1:8000",
    ):
        self.base_url = base_url.rstrip("/")

    def _get(self, path):
        response = requests.get(
            f"{self.base_url}{path}",
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def _post(self, path, data=None):
        response = requests.post(
            f"{self.base_url}{path}",
            json=data,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def _patch(self, path, data=None):
        response = requests.patch(
            f"{self.base_url}{path}",
            json=data,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def get_user(self, user_id):
        return self._get(
            f"/api/users/{user_id}"
        )

    def get_automation_settings(self, user_id):
        return self._get(
            f"/api/users/{user_id}/automation"
        )

    def get_jobs(self, user_id):
        return self._get(
            f"/api/users/{user_id}/jobs"
        )

    def create_job(self, user_id, data):
        return self._post(
            f"/api/users/{user_id}/jobs",
            data,
        )

    def get_applications(self, user_id):
        return self._get(
            f"/api/users/{user_id}/applications"
        )

    def create_application(self, user_id, data):
        return self._post(
            f"/api/users/{user_id}/applications",
            data,
        )

    def update_application(self, user_id, application_id, data):
        return self._patch(
            f"/api/users/{user_id}/applications/{application_id}",
            data,
        )

    def process_application_response(
        self,
        user_id,
        application_id,
        data,
    ):
        return self._post(
            f"/api/users/{user_id}/applications/{application_id}/response",
            data,
        )

    def start_application_follow_up(
        self,
        user_id,
        application_id,
    ):
        return self._post(
            f"/api/users/{user_id}/applications/{application_id}/follow-up",
            {},
        )

    def applications_today_count(self, user_id):
        return self._get(
            f"/api/users/{user_id}/applications/today/count"
        )

    def get_activity(self, user_id):
        return self._get(
            f"/api/users/{user_id}/activity"
        )

    def create_activity(self, user_id, data):
        return self._post(
            f"/api/users/{user_id}/activity",
            data,
        )

    def get_integrator_status(self, user_id):
        return self._get(
            f"/api/users/{user_id}/integrator"
        )

    def heartbeat(self, user_id):
        return self._post(
            f"/api/users/{user_id}/integrator/heartbeat"
        )

    def update_integrator_stats(
        self,
        user_id,
        data,
    ):
        return self._patch(
            f"/api/users/{user_id}/integrator/stats",
            data,
        )

    def health(self):
        return self._get("/api/health")
