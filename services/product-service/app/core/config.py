"""Configuration management for Product Service using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Product Service settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application Environment
    APP_ENV: str = Field(default="development", description="Environment: development, test, or production")
    LOG_LEVEL: str = Field(default="INFO", description="Logging verbosity level")

    # Network
    PORT: int = Field(default=8001, description="HTTP listening port")
    HOST: str = Field(default="0.0.0.0", description="HTTP binding host")

    # Persistence
    PRODUCT_DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/kubeshop_product",
        description="Async database connection string for Product catalog",
    )

    # Fault Simulation (for Kubernetes incident drills)
    SIMULATED_LATENCY_MS: int = Field(default=0, description="Artificial latency in milliseconds (0 = disabled)")
    SIMULATED_FAILURE_RATE: float = Field(default=0.0, description="Fraction of requests to fail artificially (0.0 = disabled)")


settings = Settings()
