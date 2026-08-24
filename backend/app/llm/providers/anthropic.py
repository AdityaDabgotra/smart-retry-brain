import json

from anthropic import AsyncAnthropic

from app.core.config import settings
from app.llm.base import LLMProvider
from app.llm.prompts import CLASSIFY_PROMPT, EXPLAIN_PROMPT


class AnthropicProvider(LLMProvider):
    def __init__(self) -> None:
        if not settings.anthropic_api_key:
            raise ValueError("RETRY_BRAIN_ANTHROPIC_API_KEY is not set")
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model

    async def _generate(self, prompt: str, temperature: float = 0.7) -> str:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=300,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in response.content if block.type == "text").strip()

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
            EXPLAIN_PROMPT.format(error_description=error_description, category=category, action=action)
        )