from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="RETRY_BRAIN_", extra="ignore")

    # App
    app_name: str = "Smart Retry Brain"
    environment: str = "development"  # development | production

    # Database
    database_url: str = "postgresql+psycopg://retry_user:retry_pass@localhost:5432/retry_brain"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # LLM
    llm_provider: str = "huggingface"  # huggingface | anthropic | openai
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"

    anthropic_api_key: str | None = None
    openai_api_key: str | None = None

    # 1 = real-time delays (production). Higher = compress delays for demo
    # (e.g. 60 -> "30 min" retry fires in 30 sec). Never changes the labels
    # shown to a merchant — only how fast wall-clock time actually passes.
    demo_time_scale: int = 60


settings = Settings()