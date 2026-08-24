from functools import lru_cache

from app.core.config import settings
from app.llm.base import LLMProvider


@lru_cache
def get_llm_provider()->LLMProvider:
    """Change settings.llm_provider to switch between different LLM providers."""

    if settings.llm_provider == "huggingface":
        from app.llm.providers.huggingface import HuggingFaceProvider
        return HuggingFaceProvider()
    
    elif settings.llm_provider == "anthropic":
        from app.llm.providers.anthropic import AnthropicProvider
        return AnthropicProvider()
    
    elif settings.llm_provider == "openai":
        from app.llm.providers.openai import OpenAIProvider
        return OpenAIProvider()
    
    raise ValueError(f"Unknown LLM provider: {settings.llm_provider}. Please check your settings.")