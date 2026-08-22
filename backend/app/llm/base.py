from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """Every LLM provider (Ollama/Qwen, Claude, OpenAI...) implements this.
    """

    @abstractmethod
    async def classify_failure(self,error_code:str,error_description:str)->dict:
        """Return {'category': str, 'confidence': float, 'reasoning': str}"""
        raise NotImplementedError
    
    @abstractmethod
    async def explain_decision(self,error_description:str,category:str,action:str)->str:
        """Return a plain-English, merchant-facing explanation string"""
        raise NotImplementedError