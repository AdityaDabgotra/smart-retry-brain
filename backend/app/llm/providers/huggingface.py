import json
import httpx

from app.core.config import settings
from app.llm.base import LLMProvider

CLASSIFY_PROMPT = """You are a payment failure classifier for a payments system.
Given an error code and description, classify it into exactly one category:
INSUFFICIENT_FUNDS, BANK_TIMEOUT, OTP_MISMATCH, CARD_EXPIRED, NETWORK_ERROR, or UNKNOWN.

Error code: {error_code}
Error description: {error_description}

Respond ONLY with valid JSON: {{"category": "...", "confidence": 0.0-1.0, "reasoning": "one short sentence"}}"""


EXPLAIN_PROMPT = """You are writing a short, plain-English note for a merchant dashboard.
The customer's payment failed. Explain why in one or two friendly, non-technical sentences,
and state what happens next.

Error description: {error_description}
Failure category: {category}
Action being taken: {action}

Respond with only the explanation text, no preamble."""


class HuggingFaceProvider(LLMProvider):
    def __init__(self)->None:
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
    

    async def _generate(self,prompt:str)->str:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt,"stream": False},
            )

            resp.raise_for_status()
            return resp.json()["response"].strip()
        
    
    async def classify_failure(self, error_code: str, error_description: str) -> dict:
        raw = await self._generate(CLASSIFY_PROMPT.format(error_code=error_code, error_description=error_description))

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"category": "UNKNOWN", "confidence": 0.0, "reasoning": "parse_failed"}
        
    
    async def explain_decision(self, error_description:str, category:str, action:str)->str:

        return await self._generate(
            EXPLAIN_PROMPT.format(
                error_description=error_description, category=category, action=action
            )
        )    