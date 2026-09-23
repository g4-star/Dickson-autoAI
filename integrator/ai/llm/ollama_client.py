import json
import logging
from typing import Any

import requests


class OllamaClient:
    """
    Small local AI client for AutoAI.

    Ollama runs locally, so candidate information does not need
    to be sent to an external AI provider.
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        model: str = "qwen2.5:3b",
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.2,
    ) -> str:

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                },
            },
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        return data.get("response", "").strip()

    def generate_json(
        self,
        prompt: str,
    ) -> dict[str, Any]:

        response = self.generate(prompt)

        # Remove accidental markdown fences.
        response = response.strip()

        if response.startswith("```"):
            response = response.replace(
                "```json",
                "",
                1,
            )

            response = response.replace(
                "```",
                "",
            ).strip()

        try:
            return json.loads(response)

        except json.JSONDecodeError as exc:
            logging.error(
                "Ollama returned invalid JSON: %s",
                response,
            )

            raise ValueError(
                "Ollama returned invalid JSON."
            ) from exc
