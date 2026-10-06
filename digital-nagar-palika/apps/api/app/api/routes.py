from fastapi import APIRouter
from fastapi import HTTPException
from sqlalchemy import text
from redis.asyncio import from_url

from app.core.config import settings
from app.core.database import engine

router = APIRouter()


@router.get("/health/live", tags=["operations"])
async def liveness():
    return {"status": "ok"}


@router.get("/health/ready", tags=["operations"])
async def readiness():
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        cache = from_url(settings.redis_url, socket_connect_timeout=1, socket_timeout=1)
        await cache.ping()
        await cache.aclose()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Service dependencies unavailable") from exc
    return {"status": "ready"}


@router.get("/public/config", tags=["public"])
async def public_config():
    return {"locales": ["mr", "hi", "en"], "defaultLocale": "mr"}
