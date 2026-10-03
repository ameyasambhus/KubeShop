"""Configuration settings for Order Service loaded from environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Order Service configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment
    APP_ENV: str = Field(default="development", description="Environment mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging verbosity")

    # Network
    PORT: int = Field(default=8002, description="HTTP listening port")
    HOST: str = Field(default="0.0.0.0", description="HTTP binding host")

    # Persistence
    ORDER_DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/kubeshop_order",
        description="Async database connection string for Order data",
    )

    # Downstream Dependency (Product Service)
    PRODUCT_SERVICE_URL: str = Field(
        default="http://localhost:8001",
        description="Base URL for Product Service discovery",
    )
    ORDER_TO_PRODUCT_TIMEOUT_SECONDS: float = Field(
        default=2.5,
        description="Explicit timeout in seconds when calling Product Service",
    )


settings = Settings()
