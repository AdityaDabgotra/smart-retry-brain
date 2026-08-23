from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.analytics import router as analytics_router
from app.api.transactions import router as transactions_router
from app.api.webhooks import router as webhooks_router

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhooks_router)
app.include_router(analytics_router)
app.include_router(transactions_router)


@app.get("/health")
async def health():
    return {"status": "ok", "environment": settings.environment, "llm_provider": settings.llm_provider}