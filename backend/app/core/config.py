import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = os.getenv("APP_NAME", "RetryBrain")
    environment: str = os.getenv("ENVIRONMENT", "development")  # development | production

    # Database
    database_url: str = os.getenv("DATABASE_URL","")

    # Redis
    redis_url: str = os.getenv("REDIS_URL", "")

    # LLM
    llm_provider: str = os.getenv("llm_provider","")  # huggingface | anthropic | openai
    ollama_base_url: str = os.getenv("ollama_base_url", "")   
    ollama_model: str = os.getenv("ollama_model", "")

    anthropic_api_key: str | None = os.getenv("anthropic_api_key", None)
    openai_api_key: str | None = os.getenv("openai_api_key", None)



settings = Settings()