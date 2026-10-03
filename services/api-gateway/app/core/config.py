"""Configuration settings for API Gateway loaded from environment variables."""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """API Gateway settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: str = Field(default="development", description="Application environment")
    LOG_LEVEL: str = Field(default="INFO", description="Logging verbosity")

    PORT: int = Field(default=8000, description="Listening port")
    HOST: str = Field(default="0.0.0.0", description="Binding host")

    # Downstream Service URLs (Configured via env, never hardcoded localhost)
    PRODUCT_SERVICE_URL: str = Field(
        default="http://localhost:8001",
        description="Base URL for routing product requests",
    )
    ORDER_SERVICE_URL: str = Field(
        default="http://localhost:8002",
        description="Base URL for routing order requests",
    )

    # Timeouts
    GATEWAY_REQUEST_TIMEOUT_SECONDS: float = Field(
        default=5.0,
        description="Overall timeout for downstream calls from the gateway",
    )

    # CORS configuration for Frontend SPA
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173", "*"],
        description="Allowed CORS origins",
    )


settings = Settings()
