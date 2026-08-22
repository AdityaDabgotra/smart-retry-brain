from functools import lru_cache

from app.core.config import settings
from app.llm.base import LLMProvider


@lru_cache
def get_llm_provider()->LLMProvider:
    """"""