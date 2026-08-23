from fastapi import FastAPI

from app.core.config import settings
from app.api.webhooks import router as webhooks_router
from app.api.analytics import router as analytics_router

app = FastAPI(title=settings.app_name)

app.include_router(webhooks_router)
app.include_router(analytics_router)


@app.get("/health")
async def health():
    return {"status": "ok", "environment": settings.environment, "llm_provider": settings.llm_provider}