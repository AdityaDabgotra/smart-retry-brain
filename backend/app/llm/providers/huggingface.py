import json
import httpx

from app.core.config import settings
from app.llm.base import LLMProvider
from app.llm.prompts import CLASSIFY_PROMPT, EXPLAIN_PROMPT


class HuggingFaceProvider(LLMProvider):
    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model

    async def _generate(self, prompt: str, temperature: float = 0.7) -> str:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": temperature},
                },
            )
            resp.raise_for_status()
            return resp.json()["response"].strip()

    async def classify_failure(self, error_code: str, error_description: str) -> dict:
        raw = await self._generate(
            CLASSIFY_PROMPT.format(error_code=error_code, error_description=error_description),
            temperature=0.0,
        )
        raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"category": "UNKNOWN", "confidence": 0.0, "reasoning": "parse_failed"}

    async def explain_decision(self, error_description: str, category: str, action: str) -> str:
        return await self._generate(
            EXPLAIN_PROMPT.format(
                error_description=error_description, category=category, action=action
            )
        )