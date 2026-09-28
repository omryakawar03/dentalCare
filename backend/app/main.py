import logging
import uuid
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from app.api.routes import auth, clinics
from app.api.errors import http_error_handler
from app.core.config import settings
from app.core.database import engine
from app.schemas.common import ErrorBody, ErrorResponse

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.JSONRenderer(),
    ],
)
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(_: FastAPI):
    app.state.redis = Redis.from_url(settings.redis_url, decode_responses=True)
    yield
    await app.state.redis.aclose()
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Multi-tenant dental clinic operations API",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    docs_url=f"{settings.api_v1_prefix}/docs",
    redoc_url=f"{settings.api_v1_prefix}/redoc",
    lifespan=lifespan,
)
app.add_exception_handler(HTTPException, http_error_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "Idempotency-Key"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    supplied_id = request.headers.get("X-Request-ID", "")
    request_id = supplied_id if len(supplied_id) <= 64 and supplied_id.replace("-", "").isalnum() else str(uuid.uuid4())
    request.state.request_id = request_id
    structlog.contextvars.bind_contextvars(request_id=request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if request.url.path.startswith(settings.api_v1_prefix):
        response.headers["Cache-Control"] = "no-store"
    structlog.contextvars.clear_contextvars()
    return response


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    fields = {".".join(str(part) for part in error["loc"]): error["msg"] for error in exc.errors()}
    request_id = getattr(request.state, "request_id", None)
    body = ErrorResponse(
        error=ErrorBody(code="VALIDATION_ERROR", message="Request validation failed", fields=fields),
        request_id=request_id,
    )
    return JSONResponse(status_code=422, content=body.model_dump(exclude_none=True))


@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", None)
    logger.exception("unhandled_request_error", path=request.url.path)
    body = ErrorResponse(
        error=ErrorBody(code="INTERNAL_ERROR", message="An unexpected error occurred"),
        request_id=request_id,
    )
    return JSONResponse(status_code=500, content=body.model_dump(exclude_none=True))


@app.get("/health/live", tags=["health"])
async def liveness():
    return {"status": "ok"}


@app.get("/health/ready", tags=["health"])
async def readiness():
    from sqlalchemy import text

    from app.core.database import SessionFactory

    async with SessionFactory() as session:
        await session.execute(text("SELECT 1"))
    await app.state.redis.ping()
    return {"status": "ready"}


app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(clinics.router, prefix=settings.api_v1_prefix)
