"""API Gateway FastAPI application entry point."""

import time
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import AppBaseException
from app.core.logging import request_id_ctx, setup_logger

logger = setup_logger(service_name="api-gateway", log_level=settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application lifecycle."""
    logger.info(
        "Starting API Gateway",
        extra={
            "env": settings.APP_ENV,
            "port": settings.PORT,
            "product_service_url": settings.PRODUCT_SERVICE_URL,
            "order_service_url": settings.ORDER_SERVICE_URL,
        },
    )
    yield
    logger.info("Shutting down API Gateway.")


app = FastAPI(
    title="KubeShop API Gateway",
    description="Single backend entry point routing frontend traffic to Product and Order microservices.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for Frontend SPA
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def correlation_and_logging_middleware(request: Request, call_next):
    """Generates X-Request-ID and logs incoming gateway traffic."""
    start_time = time.perf_counter()

    # Generate or propagate request ID
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    token = request_id_ctx.set(request_id)

    try:
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        response.headers["X-Request-ID"] = request_id

        logger.info(
            f"Gateway {request.method} {request.url.path} -> {response.status_code}",
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
            f"Unhandled exception in Gateway {request.method} {request.url.path}: {exc}",
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
    """Formats structured gateway and downstream exceptions."""
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
    """Global catch-all preventing raw tracebacks."""
    req_id = request_id_ctx.get()
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Gateway encountered an internal error",
                "request_id": req_id,
            }
        },
    )


# Mount routers
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
