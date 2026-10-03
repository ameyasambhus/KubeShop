"""Order Service FastAPI application entry point."""

import time
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import AppBaseException
from app.core.logging import request_id_ctx, setup_logger
from app.db.init_db import init_db
from app.db.session import engine

logger = setup_logger(service_name="order-service", log_level=settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application lifecycle: database startup and graceful teardown."""
    logger.info(
        "Starting Order Service",
        extra={
            "env": settings.APP_ENV,
            "port": settings.PORT,
            "product_service_url": settings.PRODUCT_SERVICE_URL,
        },
    )
    try:
        await init_db(engine)
    except Exception as exc:
        logger.error(
            "Failed to initialize database during startup: %s",
            str(exc),
            extra={"error_type": type(exc).__name__},
            exc_info=True,
        )
        if settings.APP_ENV == "production":
            raise

    yield

    logger.info("Shutting down Order Service; closing database connections.")
    await engine.dispose()


app = FastAPI(
    title="KubeShop Order Service",
    description="Microservice responsible for order creation, total calculations, and lifecycle management.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def correlation_and_logging_middleware(request: Request, call_next):
    """Propagates X-Request-ID and logs incoming requests with execution duration."""
    start_time = time.perf_counter()

    # Extract correlation ID from incoming request headers or generate a new one
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    token = request_id_ctx.set(request_id)

    try:
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Append correlation ID to response headers
        response.headers["X-Request-ID"] = request_id

        logger.info(
            f"Handled {request.method} {request.url.path} -> {response.status_code}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "request_id": request_id,
            },
        )
        return response
    except Exception as exc:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.error(
            f"Unhandled exception while processing {request.method} {request.url.path}: {exc}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": 500,
                "duration_ms": duration_ms,
                "request_id": request_id,
                "error_type": type(exc).__name__,
            },
            exc_info=True,
        )
        raise
    finally:
        request_id_ctx.reset(token)


@app.exception_handler(AppBaseException)
async def app_exception_handler(request: Request, exc: AppBaseException):
    """Formats known application exceptions into the standardized JSON error envelope."""
    req_id = exc.request_id or request_id_ctx.get()
    content = {
        "error": {
            "code": exc.code,
            "message": exc.message,
            "request_id": req_id,
        }
    }
    if exc.dependency:
        content["error"]["dependency"] = exc.dependency
    if exc.details:
        content["error"]["details"] = exc.details

    return JSONResponse(status_code=exc.status_code, content=content)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catches unhandled errors and prevents stack trace leakage in API responses."""
    req_id = request_id_ctx.get()
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred",
                "request_id": req_id,
            }
        },
    )


# Mount routes
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
