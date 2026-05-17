"""
Configuration management for the AI Email Processing System.
Handles environment variables and application settings.
"""

from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Application
    APP_NAME: str = Field(default="AI Email Processing System")
    APP_VERSION: str = Field(default="1.0.0")
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: str = Field(default="development")

    # API Configuration
    API_V1_STR: str = "/api/v1"
    API_TITLE: str = "AI Email Processing API"
    API_DESCRIPTION: str = "API for processing emails with AI"
    ALLOWED_HOSTS: list[str] = Field(default_factory=lambda: ["*"])
    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8000"]
    )

    # Database
    DATABASE_URL: str = Field(default="postgresql+asyncpg://user:password@localhost:5432/email_db")
    DB_ECHO: bool = Field(default=False)
    DB_POOL_SIZE: int = Field(default=20)
    DB_MAX_OVERFLOW: int = Field(default=10)
    DB_POOL_PRE_PING: bool = Field(default=True)

    # Authentication
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)

    # Email Configuration
    SMTP_HOST: str = Field(default="localhost")
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: Optional[str] = Field(default=None)
    SMTP_PASSWORD: Optional[str] = Field(default=None)
    SMTP_FROM_EMAIL: str = Field(default="noreply@example.com")

    # AI Configuration
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    AI_MODEL: str = Field(default="gpt-4")
    AI_REQUEST_TIMEOUT: int = Field(default=30)

    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    LOG_FILE: Optional[str] = Field(default="logs/app.log")

    # Redis (for caching and task queue)
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    REDIS_ENABLED: bool = Field(default=False)

    # Workers
    WORKERS: int = Field(default=4)

    @field_validator("CORS_ORIGINS", mode="before")
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("ALLOWED_HOSTS", mode="before")
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from comma-separated string."""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses @lru_cache for single instance across the application.
    """
    return Settings()
