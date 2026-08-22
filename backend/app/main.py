from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(title=settings.app_name)


@app.get("/health")
async def health():
    return {"status": "ok", "environment": settings.environment, "llm_provider": settings.llm_provider}